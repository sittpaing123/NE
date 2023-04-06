import asyncio
import re

from bot import Bot
from pyrogram import enums, filters, types
from pyrogram.errors import (ChannelInvalid, UsernameInvalid,
                             UsernameNotModified)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..config import Config
from ..database import a_filter
from ..utils.cache import Cache
from ..utils.logger import LOGGER

logger = LOGGER("INDEX")


lock = asyncio.Lock()
_REGEX = r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$"


@Bot.on_callback_query(filters.regex(r"^index"))  # type: ignore
async def index_files(bot: Bot, query: types.CallbackQuery):
    if query.data.startswith("index_cancel"):  # type: ignore
        Cache.CANCEL = True  # type: ignore
        return await query.answer("Cancelling Indexing")
    _, sts, chat, lst_msg_id, from_user = query.data.split("#")  # type: ignore
    if sts == "reject":
        await query.message.delete()
        await bot.send_message(
            int(from_user),
            f"Your Submission for indexing {chat} has been declined by our moderators.",
            reply_to_message_id=int(lst_msg_id),
        )
        return

    if lock.locked():
        return await query.answer("Wait until previous process complete.", show_alert=True)
    msg = query.message

    await query.answer("Processing...⏳", show_alert=True)

    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
        ),
    )
    try:
        chat = int(chat)
    except:
        chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)  # type: ignore


@Bot.on_message(((filters.forwarded & ~filters.text) | (filters.regex(_REGEX)) & filters.text) & filters.private & filters.incoming & filters.user(Config.ADMINS))  # type: ignore
async def send_for_index(bot: Bot, message: types.Message):
    if message.text:
        regex = re.compile(_REGEX)
        match = regex.match(message.text)
        if not match:
            return await message.reply("Invalid link")
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int(("-100" + chat_id))
    elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply(
            "This may be a private channel / group. Make me an admin over there to index the files."
        )
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("Invalid Link specified.")
    except Exception as e:
        logger.exception(e)
        return await message.reply(f"Errors - {e}")
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply(
            "Make Sure That Iam An Admin In The Channel, if channel is private"
        )
    if k.empty:  # type: ignore
        return await message.reply("This may be group and iam not a admin of the group.")

    if message.from_user.id in Config.ADMINS:
        buttons = [
            [
                InlineKeyboardButton(
                    "Yes",
                    callback_data=f"index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}",
                )
            ],
            [
                InlineKeyboardButton("close", callback_data="close_data"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(
            f"Do you Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>",
            reply_markup=reply_markup,
        )


@Bot.on_message(filters.command("setskip") & filters.user(Config.ADMINS))  # type: ignore
async def set_skip_number(bot: Bot, message: types.Message):
    if " " in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except:
            return await message.reply("Skip number should be an integer.")
        await message.reply(f"Successfully set SKIP number as {skip}")
        Cache.CURRENT = int(skip)  # type: ignore
    else:
        await message.reply("Give me a skip number")


async def index_files_to_db(lst_msg_id: int, chat: int, msg: types.Message, bot: Bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    async with lock:
        try:
            current = Cache.CURRENT
            Cache.CANCEL = False
            async for message in bot.iter_messages(chat, lst_msg_id, Cache.CURRENT):  # type: ignore
                if Cache.CANCEL:
                    inserted, errored = await a_filter.insert_pending()
                    if inserted:
                        total_files += inserted
                    if errored:
                        duplicate += errored
                    await msg.edit(
                        f"Successfully Cancelled!!\n\nSaved <code>{total_files} / {current}</code> files to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>"
                    )
                    break
                current += 1
                if current % 200 == 0:
                    can = [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
                    reply = InlineKeyboardMarkup(can)
                    await msg.edit_text(
                        text=f"Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>",
                        reply_markup=reply,
                    )
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [
                    enums.MessageMediaType.VIDEO,
                    enums.MessageMediaType.AUDIO,
                    enums.MessageMediaType.DOCUMENT,
                    enums.MessageMediaType.PHOTO
                ]:
                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                media.file_type = message.media.value
                if media.file_type == "photo":
                    media.file_name = message.caption
                    media.mime_type = "image/jpg"
                media.caption = message.caption
                media.chat_id = message.chat.id
                media.message_id = message.id
                inserted, errored = await a_filter.insert_many(media)
                if inserted:
                    total_files += inserted
                if errored:
                    duplicate += errored

        except Exception as e:
            logger.exception(e)
            await msg.edit(f"Error: {e}")
        else:
            inserted, errored = await a_filter.insert_pending()
            if inserted:
                total_files += inserted
            if errored:
                duplicate += errored
            await msg.edit(
                f"Successfully saved <code>{total_files} / {current}</code> to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>"
            )
