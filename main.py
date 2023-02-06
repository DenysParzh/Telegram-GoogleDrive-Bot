import asyncio
import logging
import os
import FSM
from aiogram import types, F, Bot
from aiogram.filters import Command, state
from aiogram.fsm.context import FSMContext
from googleapiclient.http import MediaFileUpload


from FSM import FileState
from Google import Create_Service
from constants import CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES
from loader import bot, dp, google_auth

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
#
# def search_file_id(file_name):
#     try:
#
#         result_file = service.files().list(q=f"name='{file_name}'").execute()
#         return result_file["files"][0]["id"]
#
#     except Exception as error:
#         print(error)
#
#
# # ------------------------------------------------------------------------------------------------------------------


@dp.message(Command(commands='add_file'))
async def add_file_message(message: types.Message, state: FSMContext):
    await message.answer("Надішліть файл для завантаженна на Google drive:")
    await state.set_state(FileState.fsm_add)


@dp.message(FileState.fsm_add, F.document)
async def add_file(message: types.Message):
    folder_id = 'root'
    #
    # file_name = message.document.file_name
    #
    # await message.answer(file_name)
    # file_path = 'D:/' + file_name

    doc = message.document.file_name

    mime_type = message.document.mime_type
    # pa =await bot.download(doc)
    # path = os.path.abspath(doc)
    await message.answer(doc)
    await message.answer(mime_type)
    await message.answer(message.document.json())
    file = bot.get_file(message.document.file_id)
    # await message.answer(str(file_info))
    file.do
    file_metadata = {
        'name': f"{doc}",
        'parents': [folder_id]
    }
    media = MediaFileUpload(doc, mimetype=mime_type)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # os.remove(file_path)
    # await state.clear()


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
