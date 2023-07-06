import asyncio
from typing import AsyncGenerator, Optional, Union

from pyrogram import types

from .client import Client
from .config import Config

from .utils.logger import LOGGER


class Bot(Client):
    def __init__(self, name: str):
        self.name = name
        self.is_idling: bool = False
        super().__init__(self.name)

    async def start(self):
        await super().start()
        await self.send_message(Config.LOG_CHANNEL, f"#START\nBot [`@{self.me.username}`] started")
        LOGGER(__name__).info("--- Bot Initialized--- ")

    async def stop(self, *args):
        await self.send_message(Config.LOG_CHANNEL, f"#STOP\nBot [`@{self.me.username}`] Stopped")
        await super().stop()

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:  # type: ignore
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            limit (``int``):
                Identifier of the last message to be returned.

            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                for message in app.iter_messages("pyrogram", 1, 15000):
                    print(message.text)
        """
        current = offset

        while self.is_idling:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(
                chat_id, list(range(current, current + new_diff + 1))
            )
            for message in messages:  # type: ignore
                yield message
                current += 1
            await asyncio.sleep(10)

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


bot = Bot(Config.BOT_NAME)  # type: ignore
