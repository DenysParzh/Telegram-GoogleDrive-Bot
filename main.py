import os
import io
from Google import Create_Service

from aiogram import executor, types
from loader import bot, dp, google_auth, drive

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from googleapiclient.http import MediaIoBaseDownload

CLIENT_SECRET_FILE = 'client_secrets.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


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
    fsm_info_folder = State()
    fsm_create_folder = State()
    fsm_delete_folder = State()
    fsm_download_folder = State()


@dp.message_handler(commands="add_file", state=None)
async def add_file_message(message: types.Message):
    await FileState.fstate.set()


@dp.message_handler(content_types=["photo"], state=FileState.fstate)
async def add_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    # file_name = message.photo[-1].as_json()
    chat_id = message.from_user.id
    caption = message.caption
    # c = message.as_json()
    # await message.answer(file_name)
    await message.answer(caption)
    # await message.answer(c)
    await message.answer(file_id)
    await bot.send_photo(chat_id=chat_id, photo=file_id)
    await state.finish()


@dp.message_handler(commands="create_folder", state=None)  # функція створення папки
async def process_create_folder(message: types.Message):
    await message.answer(f"Введіть назву папки:")
    await FileState.fsm_create_folder.set()  # стан очікування назви створеної папки


@dp.message_handler(state=FileState.fsm_create_folder)  # функція стану очікування назви створеної папки
async def create_folder(message: types.Message, state: FSMContext):
    file_metadata = {
        'name': message.text,  # назва папки (вводится через телеграм)
        'mimeType': 'application/vnd.google-apps.folder',
        # 'parents': []
    }
    service.files().create(body=file_metadata).execute()  # створення нової пустої папки
    await message.answer(f"Папка успішно створена.")
    await state.finish()


@dp.message_handler(commands="delete_folder", state=None)  # функція видалення папки або файлу по id
async def add_file_message(message: types.Message):
    await message.answer(f"Введите id папки которую хотите удалить:")
    await FileState.fsm_delete_folder.set()


@dp.message_handler(state=FileState.fsm_delete_folder)
async def add_photo(message: types.Message, state: FSMContext):
    file_id = message.text  # введений id файлу/папки
    service.files().delete(fileId=file_id).execute()  # видалення папки або файлу по id
    await message.answer(f"Папка успішно видалена.")
    await state.finish()


@dp.message_handler(commands="download", state=None)  # функція завантаження, (функціонал у розробці)
async def download_file(message: types.Message):
    await message.answer(f"Введите id папки которую хотите скачать:")
    await FileState.fsm_download_folder.set()


# @dp.message_handler(state=FileState.fsm_download_folder)
# async def add_photo(message: types.Message, state: FSMContext):
#     file6 = drive.CreateFile({'id': ['id']})
#     file6.GetContentFile('catlove.png')

@dp.message_handler(commands="info", state=None)  # функція завантаження, (функціонал у розробці)
async def info_file(message: types.Message):
    fileList = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file in fileList:
        await message.answer('Title: %s, ID: %s' % (file['title'], file['id']))
        # Get the folder ID that you want


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
