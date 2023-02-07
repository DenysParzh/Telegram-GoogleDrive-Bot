import asyncio
import logging
import os
import typing

from aiogram import types, F
from aiogram.filters import Command, state
from aiogram.fsm.context import FSMContext
from googleapiclient.http import MediaFileUpload

from FSM import FileState
from Google import Create_Service
from constants import CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES
from loader import bot, dp, google_auth, drive

from google.auth.transport import requests

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
logging.basicConfig(level=logging.INFO)


# ------------------------------------------------------------------------------------------------------------------

@dp.message(Command(commands='start'))
async def process_start_command(message: types.Message):
    await message.answer(f"Привет {message.from_user.first_name}!\nНапиши мне что-нибудь!")


# ------------------------------------------------------------------------------------------------------------------
@dp.message(Command(commands='login'))
async def user_login(message: types.Message) -> None:
    try:
        google_auth.LocalWebserverAuth()

        await message.answer("Вы залогинились")
    except Exception as ex_info:
        print(f"Інформація про помилку: {ex_info}")


# # ------------------------------------------------------------------------------------------------------------------

def search_file_id(file_name):
    try:

        result_file = service.files().list(q=f"name='{file_name}'").execute()
        return result_file["files"][0]["id"]

    except Exception as error:
        print(error)


def search_file(file_name):
    path = 'D:/'
    for rootdir, dirs, files in os.walk(path):
        for file in files:
            if (file == file_name):
                path = os.path.join(rootdir, file)
                return path

    path = 'C:/'
    for rootdir, dirs, files in os.walk(path):
        for file in files:
            if (file == file_name):
                path = os.path.join(rootdir, file)
                return path

# # ------------------------------------------------------------------------------------------------------------------

@dp.message(Command(commands='add_file'))
async def add_file_message(message: types.Message, state: FSMContext):
    # await message.answer("Надішліть файл для завантаженна на Google drive:")
    await message.answer("Введіть назву папки в яку ви хочете завантажити файл:")
    await state.set_state(FileState.fsm_add)


@dp.message(FileState.fsm_add)
async def add_file_name(message: types.Message, state: FSMContext):
    # await message.answer("Введіть назву папки в яку ви хочете завантажити файл:")

    file_id = search_file_id(message.text)
    await state.update_data(file_id=file_id)
    # await message.answer(file_id)
    await message.answer("Надішліть файл для завантаженна на Google drive:")
    await state.set_state(FileState.fsm_add_name_file)


@dp.message(FileState.fsm_add_name_file, F.document)
async def add_file(message: types.Message, state: FSMContext):

    data = await state.get_data()
    folder_id = data['file_id']
    # await message.answer(folder_id)
    file_name = message.document.file_name
    path = search_file(file_name)

    # await message.answer(path)
    filepath = path.replace('\\', '/')
    # folder_id = name_folder
    file_name = message.document.file_name
    # await message.answer(file_name)
    file_metadata = {
        'name': file_name,
        'parents': ['root' if folder_id is None else folder_id]
    }
    media = MediaFileUpload(filepath, resumable=True)
    r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()


# # ------------------------------------------------------------------------------------------------------------------
# @dp.message(commands="create_folder", state=None)  # функція створення папки
# async def process_create_folder(message: types.Message):
#     await message.answer(f"Введіть назву папки:")
#     await FileState.fsm_create_folder.set()  # стан очікування назви створеної папки
#
#
# @dp.message(state=FileState.fsm_create_folder)  # функція стану очікування назви створеної папки
# async def create_folder(message: types.Message, state: FSMContext):
#     name_folder = message.text
#     async with state.proxy() as data:
#         data['name_folder'] = name_folder
#     await message.answer(
#         f"Введіть назву папки у якій хочете створити папку, або напищіть root,щоб створення відбулося в корінній папці:")
#     await FileState.fsm_choice_create_folder.set()
#
#
# @dp.message(state=FileState.fsm_choice_create_folder)  # функція стану очікування назви створеної папки
# async def create_folder(message: types.Message, state: FSMContext):
#     try:
#         file_id = search_file_id(message.text)
#         async with state.proxy() as data:
#             name_folder = data['name_folder']
#
#         file_metadata = {
#             'name': name_folder,  # назва папки (вводится через телеграм)
#             'mimeType': 'application/vnd.google-apps.folder',
#             'parents': ['root' if file_id is None else file_id]
#         }
#         service.files().create(body=file_metadata).execute()  # створення нової пустої папки
#         await message.answer(f"Папка успішно створена.")
#         await state.finish()
#     except Exception as ex:
#         print(ex)
#
#
# # ------------------------------------------------------------------------------------------------------------------
# @dp.message(commands="delete_folder", state=None)  # функція видалення папки або файлу по id
# async def file_delete_message(message: types.Message):
#     await message.answer(f"Введіть назву файлу для видалення:")
#     await FileState.fsm_delete.set()
#
#
# @dp.message(state=FileState.fsm_delete)
# async def file_delete(message: types.Message, state: FSMContext):
#     file_id = search_file_id(message.text)  #
#     service.files().delete(fileId=file_id).execute()  # видалення папки або файлу по id
#
#     await message.answer(f"Папка успішно видалена.")
#     await state.finish()
#
#
# # ------------------------------------------------------------------------------------------------------------------
# @dp.message(commands="download", state=None)  # функція завантаження, (функціонал у розробці)
# async def download_file(message: types.Message):
#     await message.answer(f"Введіть назву файлу, який бажаете завантажити:")
#     await FileState.fsm_download.set()
#
#
# @dp.message(state=FileState.fsm_download)
# async def download(message: types.Message, state: FSMContext):
#     file_name = message.text
#     file_id = search_file_id(file_name)
#
#     request = service.files().get_media(fileId=file_id)
#
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fd=fh, request=request)
#
#     done = False
#
#     while not done:
#         status, done = downloader.next_chunk()
#         await message.answer(f'Download progress...')
#     fh.seek(0)
#     with open(os.path.join('D:/', file_name), 'wb') as f:
#         f.write(fh.read())
#         f.close()
#
#     await message.reply_document(open(os.path.join('D:/', file_name), 'rb'))
#     await message.answer(f"Файл завантажен.")
#     path = os.path.join('D:/', file_name)
#     os.remove(path)
#     await state.finish()
#
#
# # ------------------------------------------------------------------------------------------------------------------
# @dp.message(commands="info", state=None)  # функція завантаження, (функціонал у розробці)
# async def info_file(message: types.Message):
#     await message.answer(
#         "Введите имя папки о содержании которой хотите получить информацию, если хотите осмотреть только коренную папку введите root")
#     await FileState.fsm_info.set()
#
#
# @dp.message(state=FileState.fsm_info)
# async def info_file(message: types.Message, state: FSMContext):
#     fileList = drive.ListFile({'q': f"'{search_file_id(message.text)}' in parents and trashed=false"}).GetList()
#     for file in fileList:
#         await message.answer('Назва: %s' % (file['title']))
#
#     await state.finish()
#

# ------------------------------------------------------------------------------------------------------------------

# if __name__ == '__main__':
#     #executor.start_polling(dp, skip_updates=True)
#     #main()
#     dp.start_polling(dp, skip_updates=True)


async def main():
    # dp.message.register(process_start_command) # старт
    # dp.message.register(user_login)  # логін
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
