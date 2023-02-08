import asyncio
import logging
import os
import io

from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from aiogram.types import FSInputFile

from FSM import FileState
from Google import Create_Service
from constants import CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES, CACHE_FOLDER_NAME
from loader import bot, dp, google_auth

from keyboards.reply import button_stop

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
    file_metadata = {
        'name': f"{file_name}",
        'parents': ['root' if folder_id is None else folder_id]
    }

    await bot.download(file_id, abs_path)
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
    await message.answer("⬇️ Надішліть файл/файли для завантаження ⬇️")
    await message.answer("Якщо хочете припинити завантажувати файли введіть stop", reply_markup=button_stop)
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
    mime_type = f'image/{photo_name.split(".")[-1]}'

    await upload_file(photo_name, mime_type, folder_id, photo_id)


@dp.message(FileState.fsm_upload, F.video)
async def upload_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    video_name = message.video.file_name
    mime_type = message.video.mime_type
    video_id = message.video.file_id

    await upload_file(video_name, mime_type, folder_id, video_id)


@dp.message(FileState.fsm_upload, F.voice)
async def upload_voice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    voice_id = message.voice.file_id
    voice_info = await bot.get_file(voice_id)
    voice_name = voice_info.file_path.split('/')[-1]

    voice_id = message.voice.file_id
    mime_type = message.voice.mime_type

    await upload_file(voice_name, mime_type, folder_id, voice_id)


@dp.message(FileState.fsm_upload, F.audio)
async def upload_audio(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    audio_name = message.audio.file_name
    mime_type = message.audio.mime_type
    audio_id = message.audio.file_id

    await upload_file(audio_name, mime_type, folder_id, audio_id)


@dp.message(FileState.fsm_upload, F.video_note)
async def upload_video_node(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    video_note_id = message.video_note.file_id
    video_note_info = await bot.get_file(video_note_id)
    video_note_name = video_note_info.file_path.split('/')[-1]
    mime_type = "video/mp4"

    await upload_file(video_note_name, mime_type, folder_id, video_note_id)


@dp.message(FileState.fsm_upload, F.animation)
async def upload_audio(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    animation_name = message.animation.file_name
    mime_type = message.animation.mime_type
    animation_id = message.animation.file_id

    await upload_file(animation_name, mime_type, folder_id, animation_id)


@dp.message(Command(commands='stop'))
async def upload_video_node(message: types.Message, state: FSMContext):
    await state.clear()


# ------------------------------------------------------------------------------------------------------------------
@dp.message(Command(commands="create"))  # функція створення папки
async def process_create_folder(message: types.Message, state: FSMContext):
    await message.answer(
        f"Введіть назву папки у якій хочете створити папку, або напищіть root,щоб створення відбулося в корінній папці:",
        reply_markup=button_stop)
    await state.set_state(FileState.fsm_create_folder)  # стан очікування назви створеної папки


@dp.message(FileState.fsm_create_folder)  # функція стану очікування назви створеної папки
async def create_folder(message: types.Message, state: FSMContext):
    folder_choice_name = message.text
    await state.update_data(folder_choice_name=folder_choice_name)

    await message.answer(f"Введіть назву папки:")
    await state.set_state(FileState.fsm_choice_create_folder)


@dp.message(FileState.fsm_choice_create_folder)  # функція стану очікування назви створеної папки
async def create_folder(message: types.Message, state: FSMContext):
    try:

        folder_name = message.text

        data = await state.get_data()

        file_id = search_file_id(data["folder_choice_name"])

        file_metadata = {
            'name': folder_name,  # назва папки (вводится через телеграм)
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': ['root' if file_id is None else file_id]
        }

        service.files().create(body=file_metadata).execute()  # створення нової пустої папки
        await message.answer(
            f"Папка успішно створена. Якщо хочете додати ще папку, введіть назву, якщо ні введіть stop:")

    except Exception as ex:
        print(ex)


#
# # ------------------------------------------------------------------------------------------------------------------
@dp.message(Command(commands="delete"))  # функція видалення папки або файлу по id
async def file_delete_message(message: types.Message, state: FSMContext):
    await message.answer(f"Введіть назву файлу для видалення:")
    await message.answer("Якщо хочете зупинити виделення введіть \stop:", reply_markup=button_stop)
    await state.set_state(FileState.fsm_delete)


@dp.message(FileState.fsm_delete)
async def file_delete(message: types.Message, state: FSMContext):
    file_id = search_file_id(message.text)  #
    service.files().delete(fileId=file_id).execute()  # видалення папки або файлу по id

    await message.answer(f"Папка успішно видалена.")


# # ------------------------------------------------------------------------------------------------------------------
@dp.message(Command(commands="download"))  # функція завантаження, (функціонал у розробці)
async def download_message(message: types.Message, state: FSMContext):
    await message.answer(f"Введіть назву файлу, який бажаете завантажити:")
    await state.set_state(FileState.fsm_download)


@dp.message(FileState.fsm_download)
async def download(message: types.Message, state: FSMContext):
    try:
        await message.answer(reply_markup=button_stop)
        file_name = message.text
        file_id = search_file_id(file_name)
        abs_path = f"{CACHE_FOLDER_NAME}\\{file_name}"

        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(fd=file, request=request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            await message.answer(f'Download...')

        file.seek(0)
        with open(abs_path, "wb") as new_file:
            new_file.write(file.read())
            file.close()

        cache_file = FSInputFile(abs_path, filename=file_name)
        await bot.send_document(message.chat.id, document=cache_file)

        os.remove(abs_path)

    except Exception as error:
        await message.answer(F' {error}')
    finally:
        await state.clear()


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
