from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from app.data.ClickHouse.metrics import log_unique_user, log_metrics, get_user_history, clear_user_history
from app.data.config import WAITING_MESSAGE
from app.keyboards.base import kb_start_menu, kb_back, kb_yes_no
from app.states.user_states import Messages
from app.loader import dp, bot
from app.models.OpenAi import gpt_4o_mini, summarize_context
from app.utils.filters import IsFollower
from app.utils.text_changes import replace_bold_with_html
from app.utils.misc import rate_limit
from app_logging import logger


@rate_limit(5, key='start')
@dp.message_handler(Command('start'), state="*")
async def start_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await log_unique_user(user_id)

    await message.answer(text='Это Chat GPT для пользователей Liberty.', reply_markup=kb_start_menu)
    await state.finish()


@dp.callback_query_handler(text="start_menu", state="*")
async def start_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Это Chat GPT для пользователей Liberty.', reply_markup=kb_start_menu)
    await state.finish()


@rate_limit(limit=5, key='new_chat')
@dp.callback_query_handler(IsFollower(), text='new_chat', state='*')
async def new_chat(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Начните диалог с чатом", reply_markup=kb_back)
    await Messages.new_message.set()


@rate_limit(limit=5, key='continue_chat')
@dp.message_handler(IsFollower(), state=Messages.new_message)
async def continue_chat(message: types.Message, state: FSMContext):
    try:
        waiting_message = await message.answer(text=WAITING_MESSAGE)
        user_id = message.from_user.id

        # Working with history, making right format
        history = await get_user_history(user_id=user_id)
        history = [{'role': 'assistant', 'content': history}] if history else []
        history.append({'role': 'user', 'content': message.text})

        # Sending request and message to user
        text = await gpt_4o_mini(history)
        await bot.delete_message(chat_id=message.chat.id, message_id=waiting_message.message_id)
        await message.answer(text=text, parse_mode=types.ParseMode.MARKDOWN)

        # Making summarization
        history.append({'role': 'assistant', 'content': replace_bold_with_html(text)})

        summary = await summarize_context(history)

        # Adding info to metrics
        await log_metrics(user_id,
                          count_requests=1,
                          count_words_requests=len(message.text.split(' ')),
                          count_words_response=len(text.split(' ')),
                          history=summary)

        # Passing state to continue
        await Messages.new_message.set()

    except Exception as e:
        await message.answer(text='Возникла ошибка, повторите еще раз позже\n\n'
                                  'Если ошибка повторяется, обратитесь в @liberty_support')
        logger.error(f'Error occurred in "continue_chat": {e}')


@dp.callback_query_handler(IsFollower(), text='clear_user_history', state='*')
async def clear_users_history(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Вы уверены что хотите стереть историю общения с ботом?', reply_markup=kb_yes_no)


@dp.callback_query_handler(IsFollower(), text='yes_choice', state='*')
async def yes_choice(call: types.CallbackQuery, state: FSMContext):
    result = await clear_user_history(call.from_user.id)
    if not result:
        await call.message.answer(text='Возникла ошибка с отчисткой истории')
        return
    await call.message.edit_text(text='История отчищена успешно', reply_markup=kb_back)
