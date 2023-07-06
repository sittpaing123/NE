from typing import Union

from pyrogram import handlers, types

from .client import PatchedClient


async def resolve_listener(
    client: PatchedClient,
    update: Union[types.CallbackQuery, types.Message, types.InlineQuery, types.ChosenInlineResult],
):
    if isinstance(update, types.CallbackQuery):
        if update.message:
            key = f"{update.message.chat.id}:{update.message.id}"
        elif update.inline_message_id:
            key = update.inline_message_id
        else:
            return
    elif isinstance(update, (types.ChosenInlineResult, types.InlineQuery)):
        key = str(update.from_user.id)
    else:
        key = str(update.chat.id)  # type: ignore

    listener = client.listeners.get(key)

    if listener and not listener["future"].done():  # type: ignore
        if callable(listener["filters"]):
            if not await listener["filters"](client, update):
                update.continue_propagation()
        listener["future"].set_result(update)  # type: ignore
        update.stop_propagation()
    else:
        if listener and listener["future"].done():  # type: ignore
            client.remove_listener(key, listener["future"])


class Client(PatchedClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def start(self, *args, **kwargs):
        self.add_handler(handlers.CallbackQueryHandler(resolve_listener), group=-2)
        self.add_handler(handlers.InlineQueryHandler(resolve_listener), group=-2)
        self.add_handler(handlers.ChosenInlineResultHandler(resolve_listener), group=-2)
        self.add_handler(handlers.MessageHandler(resolve_listener), group=-2)
        await super().start(*args, **kwargs)

    async def iter_chat_history(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset_id: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through chat history sequentially.
        This method iterates through the chat history in chronological order, starting from the specified offset_id.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages), you can simply use "me" or "self".
                For a contact that exists in your Telegram address book, you can use their phone number (str).
            limit (``int``):
                Maximum number of messages to be returned.
            offset_id (``int``, *optional*):
                Identifier of the message to start from.
                Defaults to 0, which means the beginning of the chat history.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                async for message in app.iter_chat_history("pyrogram", 100, offset_id=15000):
                    print(message.text)
        """
        current = offset_id
        while self.is_idling:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_chat_history(
                chat_id,
                limit=new_diff,
                offset_id=current,
                reverse=True
            )
            for message in messages:
                yield message
                current = message.message_id - 1
            await asyncio.sleep(10)
