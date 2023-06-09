from pyrogram import Client, filters, enums
from clone_plugins.info import INDEX_CHANNELS
from clone_plugins.database.ia_filterdb import save_file

media_filter = filters.document | filters.video


@Client.on_message(filters.chat(INDEX_CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    media = getattr(message, message.media.value, None)
    media.file_type = message.media.value
    media.caption = message.caption
    await save_file(media)
