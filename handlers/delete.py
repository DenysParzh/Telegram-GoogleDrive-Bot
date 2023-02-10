from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from FSM import FileState
from keyboards.reply import button_stop
from loader import service
from gdrive_utils.scripts import search_file_id

router = Router()


@router.message(Command(commands="delete"))  # функція видалення папки або файлу по id
async def file_delete_message(message: types.Message, state: FSMContext):
    await message.answer(f"Введіть назву файлу для видалення:")
    await message.answer("Якщо хочете зупинити виделення введіть \stop:",reply_markup=button_stop)  # reply_markup=button_stop
    await state.set_state(FileState.fsm_delete)


@router.message(FileState.fsm_delete)
async def file_delete(message: types.Message, state: FSMContext):
    file_id = search_file_id(message.text)  #
    service.files().delete(fileId=file_id).execute()  # видалення папки або файлу по id

    await message.answer(f"Папка успішно видалена.")
