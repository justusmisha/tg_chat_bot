from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from app.loader import redis_client


class IsFollower(BoundFilter):
    async def check(self, message: types.Message):
        user_id = message.from_user.id
        result = await redis_client.get_value(f'gptsubscription:{user_id}')
        if not result or result is None:
            await message.answer('Вы не являетесь владельцем ни одной подписки Liberty.')
            return False
        return True
