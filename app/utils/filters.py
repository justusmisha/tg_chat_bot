from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from app.api.endpoints import Endpoints
from app.loader import api_client


class IsFollower(BoundFilter):
    async def check(self, message: types.Message):
        user_id = message.from_user.id
        result = await api_client.get(Endpoints.get_user_subscription, user_id=user_id)
        if not result or result is None:
            await message.answer('Вы не являетесь владельцем ни одной подписки Liberty.\n\nДля того чтобы приобрести ее, перейдите в бота @vpn_liberty_bot и приобретите любую подписку.')
            return False
        return True
