from aiogram import types

kb_start_menu = types.InlineKeyboardMarkup()
kb_start_menu.row(types.InlineKeyboardButton(text='🤖 Начать чат', callback_data='new_chat'),
                  types.InlineKeyboardButton(text='🗑 Стереть историю', callback_data='clear_user_history'))
kb_start_menu.row(types.InlineKeyboardButton(text='🤝 Поддержка', url='https://t.me/liberty_bot_support'),
                  types.InlineKeyboardButton(text='💰 Создать подписку', url='https://t.me/vpn_liberty_bot'),
                  )

kb_back = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(text='⬅️ Назад в меню', callback_data='start_menu'))

kb_yes_no = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(text='Да', callback_data='yes_choice'),
    types.InlineKeyboardButton(text='Нет', callback_data='start_menu'),
)
