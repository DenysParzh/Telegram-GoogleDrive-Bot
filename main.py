from Google import Create_Service
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from loader import bot, dp, google_auth, drive

from aiogram.types import InputFile

from FSM import FileState
from constants import CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES
import os
import io
from googleapiclient.http import MediaIoBaseDownload

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(f"Привет {message.from_user.first_name}!\nНапиши мне что-нибудь!")


@dp.message_handler(commands=['login'])
async def user_login(message: types.Message) -> None:
    try:
        google_auth.LocalWebserverAuth()
        await message.answer("Вы залогинились")
    except Exception as ex_info:
        print(f"Інформація про помилку: {ex_info}")


@dp.message_handler(commands="add_file", state=None)
async def add_file_message(message: types.Message):
    await FileState.fsm_photo.set()


@dp.message_handler(content_types=["photo"], state=FileState.fsm_photo)
async def add_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    chat_id = message.from_user.id
    caption = message.caption

    await message.answer(caption)
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
        'mimeType': 'application/vnd.google-apps.folder'
        # 'parents': []
    }
    service.files().create(body=file_metadata).execute()  # створення нової пустої папки
    await message.answer(f"Папка успішно створена.")
    await state.finish()


@dp.message_handler(commands="delete_folder", state=None)  # функція видалення папки або файлу по id
async def file_delete_message(message: types.Message):
    await message.answer(f"Введите id папки которую хотите удалить:")
    await FileState.fsm_delete.set()


def search_file_name(file_name):
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

    for file in file_list:
        if file['title'] == file_name:
            return file['id']

    return file_list[0]['id']  # Обробити виключення: якщо файл не знайдено


@dp.message_handler(state=FileState.fsm_delete)
async def file_delete(message: types.Message, state: FSMContext):
    file_id = search_file_name(message.text)  #
    service.files().delete(fileId=file_id).execute()  # видалення папки або файлу по id

    await message.answer(f"Папка успішно видалена.")
    await state.finish()


@dp.message_handler(commands="download", state=None)  # функція завантаження, (функціонал у розробці)
async def download_file(message: types.Message):
    await message.answer(f"Введіть назву файлу, яку бажаете завантажити:")
    await FileState.fsm_download.set()


@dp.message_handler(state=FileState.fsm_download)
async def download_file(message: types.Message, state: FSMContext):
    file_name = message.text
    file_id = search_file_name(file_name)

    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)

    done = False

    while not done:
        status, done = downloader.next_chunk()
        await message.answer(f'Download progress{0}'.format(status.progress() * 100))
    fh.seek(0)
    with open(os.path.join('D:/', file_name), 'wb') as f:
        f.write(fh.read())
        f.close()

    photo = InputFile(f"D:/{file_name}")
    await bot.send_photo(chat_id=message.chat.id, photo=photo)

    #await message.reply_document(open(os.path.join('D:/', file_name), 'rb'))
    await message.answer(f"Файл завантажен.")
    path = os.path.join('D:/', file_name)
    os.remove(path)
    await state.finish()


@dp.message_handler(commands="info", state=None)  # функція завантаження, (функціонал у розробці)
async def info_file(message: types.Message):
    fileList = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file in fileList:
        await message.answer('Title: %s, ID: %s' % (file['title'], file['id']))
        # Get the folder ID that you want


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
