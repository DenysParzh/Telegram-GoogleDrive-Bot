from aiogram import executor, types
from loader import bot, dp, google_auth

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(f"Привет {message.from_user.first_name}!\nНапиши мне что-нибудь!")


@dp.message_handler(commands=['login'])
async def user_login(message: types.Message) -> None:
    try:
        google_auth.LocalWebserverAuth()
    except Exception as ex_info:
        print(f"Інформація про помилку: {ex_info}")


class FileState(StatesGroup):
    fstate = State()


@dp.message_handler(commands="add_file", state=None)
async def add_file_message(message: types.Message):
    await FileState.fstate.set()


@dp.message_handler(content_types=["photo"], state=FileState.fstate)
async def add_photo(message: types.Message, state: FSMContext):

    file_id = message.photo[-1].file_id
    chat_id = message.from_user.id

    await bot.send_photo(chat_id=chat_id, photo=file_id)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
