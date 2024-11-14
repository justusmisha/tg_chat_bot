import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

from app.loader import bot


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """
        This handler is called when dispatcher receives a message

        :param message:
        """
        # Get current handler
        handler = current_handler.get()

        # Get dispatcher from context
        dispatcher = Dispatcher.get_current()
        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        # Use Dispatcher.throttle method.
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # Execute action
            await self.message_throttled(message, t)

            # Cancel current handler
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        """
        Notify user only on first exceed and notify about unlocking only on last exceed

        :param message:
        :param throttled:
        """
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            key = f"{self.prefix}_message"

        # message_wait = None

        # Calculate how many time is left till the block ends
        delta = throttled.rate - throttled.delta

        # Prevent flooding
        if throttled.exceeded_count <= 2:
            message_wait = await message.reply('⏳ Подождите несколько секунд перед тем, как отправить следующий вопрос . . .')
        else:
            message_wait = None

        # Sleep.
        await asyncio.sleep(delta)

        # Check lock status
        thr = await dispatcher.check_key(key)

        if thr.exceeded_count == throttled.exceeded_count:
            if message_wait is not None:
                await message_wait.delete()
            await message.reply('Можете задать следующий вопрос')

    async def on_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_callback"

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.callback_query_throttled(callback_query, t)
            raise CancelHandler()

    async def callback_query_throttled(self, callback_query: types.CallbackQuery, throttled: Throttled):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            key = f"{self.prefix}_callback"

        delta = throttled.rate - throttled.delta

        if throttled.exceeded_count <= 1:
            await callback_query.message.answer('Вы нажимете слишком часто! Подождите пару секунд и вы будете разблокированы')

        await asyncio.sleep(delta)
        thr = await dispatcher.check_key(key)

        if thr.exceeded_count == throttled.exceeded_count:
            await callback_query.message.answer('Вы разблокированы!')
