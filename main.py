import asyncio
import logging
import os

from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from googleapiclient.http import MediaFileUpload

from FSM import FileState
from Google import Create_Service
from constants import CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES, CACHE_FOLDER_NAME
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

def search_file_id(file_name):
    try:

        result_file = service.files().list(q=f"name='{file_name}'").execute()
        return result_file["files"][0]["id"]

    except Exception as error:
        print(error)


async def upload_file(file_name, mimeType, folder_id, file_id):
    abs_path = f"{CACHE_FOLDER_NAME}\\{file_name}"
    await bot.download(file_id, abs_path)
    file_metadata = {
        'name': f"{file_name}",
        'parents': ['root' if folder_id is None else folder_id]
    }

    media = MediaFileUpload(abs_path, mimetype=mimeType)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    media.__del__()
    os.remove(abs_path)


# # ------------------------------------------------------------------------------------------------------------------

@dp.message(Command(commands='upload'))
async def upload_message(message: types.Message, state: FSMContext):
    await message.answer("⬇️ Введіть назву папки на Google Drive ⬇️")
    await state.set_state(FileState.fsm_upload_folder_name)


@dp.message(FileState.fsm_upload_folder_name)
async def upload_folder_name(message: types.Message, state: FSMContext):
    folder_id = search_file_id(message.text)
    await state.update_data(folder_id=folder_id)
    await message.answer("⬇️ Надішліть один файл для завантаження ⬇️")
    await state.set_state(FileState.fsm_upload)


@dp.message(FileState.fsm_upload, F.document)
async def upload_document(message: types.Message, state: FSMContext):
    if not os.path.exists(CACHE_FOLDER_NAME):
        os.mkdir(CACHE_FOLDER_NAME)

    data = await state.get_data()
    folder_id = data["folder_id"]

    file_name = message.document.file_name
    file_id = message.document.file_id
    mime_type = message.document.mime_type
    await upload_file(file_name, mime_type, folder_id, file_id)


@dp.message(FileState.fsm_upload, F.photo)
async def upload_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    photo_id = message.photo[-1].file_id
    photo_info = await bot.get_file(photo_id)
    photo_name = photo_info.file_path.split('/')[-1]
    mime_type = 'image/jpeg'

    await upload_file(photo_name, mime_type, folder_id, photo_id)


@dp.message(FileState.fsm_upload, F.video)
async def upload_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    video_name = message.video.file_name
    mime_type = message.video.mime_type
    video_id = message.video.file_id  # Get file id

    await upload_file(video_name, mime_type, folder_id, video_id)


@dp.message(FileState.fsm_upload, F.voice)
async def upload_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    voice_id = message.voice.file_id
    voice_info = await bot.get_file(voice_id)
    voice_name = voice_info.file_path.split('/')[-1]

    voice_id = message.voice.file_id
    mime_type = message.voice.mime_type

    await upload_file(voice_name, mime_type, folder_id, voice_id)


@dp.message(FileState.fsm_upload, F.audio)
async def upload_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    audio_name = message.audio.file_name
    mime_type = message.audio.mime_type
    audio_id = message.audio.file_id  # Get file id

    await upload_file(audio_name, mime_type, folder_id, audio_id)


# ------------------------------------------------------------------------------------------------------------------
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

async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
