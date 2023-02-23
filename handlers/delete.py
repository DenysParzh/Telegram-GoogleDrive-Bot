from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.FSM import FileState
from keyboards.reply import button_stop
from gdrive.google import GoogleDrive

router = Router()


# функція видалення папки або файлу по id
@router.message(Command(commands="delete"))
async def file_delete_message(message: types.Message, state: FSMContext):
    await message.answer("⬇️ Введіть назву файлу для видалення ⬇️")
    await message.answer("Нажміть stop для зупинки", reply_markup=button_stop)
    await state.set_state(FileState.fsm_delete)


@router.message(FileState.fsm_delete)
async def file_delete(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    file_name = message.text
    message_for_user = GoogleDrive(user_id).delete_file(file_name)

    await message.answer(f"{message_for_user}")
