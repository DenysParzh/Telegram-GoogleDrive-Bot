from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import service
from utils.FSM import FileState
from keyboards.reply import button_stop
from gdrive.scripts import search_file_id

router = Router()


@router.message(Command(commands="create"))  # функція створення папки
async def process_create_folder(message: types.Message, state: FSMContext):
    await message.answer(
        "Введіть назву папки у якій хочете створити папку, "
        "або напищіть root,щоб створення відбулося в корінній папці:",
        reply_markup=button_stop
    )
    await state.set_state(FileState.fsm_create_folder)  # стан очікування назви створеної папки


@router.message(FileState.fsm_create_folder)
async def create_folder(message: types.Message, state: FSMContext):
    folder_choice_name = message.text
    await state.update_data(folder_choice_name=folder_choice_name)

    await message.answer("Введіть назву папки:")
    await state.set_state(FileState.fsm_choice_create_folder)


@router.message(FileState.fsm_choice_create_folder)  # функція стану очікування назви створеної папки
async def create_folder(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        file_id = search_file_id(data["folder_choice_name"])

        folder_name = message.text
        file_metadata = {
            'name': folder_name,  # назва папки (вводится через телеграм)
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': ['root' if file_id is None else file_id]
        }

        service.files().create(body=file_metadata).execute()  # створення нової пустої папки
        await message.answer(
            "Папка успішно створена. Якщо хочете додати ще"
            " папку, введіть назву, якщо ні введіть stop:")

    except Exception as ex:
        print(ex)
