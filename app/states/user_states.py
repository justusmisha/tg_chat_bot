from aiogram.dispatcher.filters.state import State, StatesGroup


class Messages(StatesGroup):
    new_message = State()