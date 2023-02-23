from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.FSM import FileState
from gdrive.google import GoogleDrive
from keyboards.reply import button_stop

router = Router()


@router.message(Command(commands="create"))  # функція створення папки
async def process_create_folder(message: types.Message, state: FSMContext):
    await message.answer(
        "⬇️ Введіть назву папки, у якій хочете створити папку ⬇️",
        reply_markup=button_stop
    )
    await state.set_state(FileState.fsm_create_folder)  # стан очікування назви створеної папки


@router.message(FileState.fsm_create_folder)
async def create_folder(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = GoogleDrive(user_id)
    parent_folder_name = message.text
    parent_folder_id = user_data.search_id(parent_folder_name)

    await state.update_data(user_data=user_data,
                            parent_folder_id=parent_folder_id)

    await message.answer("Введіть назву папки:")
    await state.set_state(FileState.fsm_choice_create_folder)


@router.message(FileState.fsm_choice_create_folder)  # функція стану очікування назви створеної папки
async def create_folder(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_data = data["user_data"]
    parent_folder_id = data["parent_folder_id"]

    folder_name = message.text
    user_data.create_folder(folder_name, parent_folder_id)

    await message.answer("✅ Папка успішно створена ✅")
