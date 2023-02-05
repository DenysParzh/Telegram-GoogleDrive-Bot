from Google import Create_Service
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from loader import bot, dp, google_auth, drive

from FSM import FileState
from constants import CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES
import os
import io
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


# ------------------------------------------------------------------------------------------------------------------
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(f"Привет {message.from_user.first_name}!\nНапиши мне что-нибудь!")


# ------------------------------------------------------------------------------------------------------------------
@dp.message_handler(commands=['login'])
async def user_login(message: types.Message) -> None:
    try:
        google_auth.LocalWebserverAuth()
        await message.answer("Вы залогинились")
    except Exception as ex_info:
        print(f"Інформація про помилку: {ex_info}")


# ------------------------------------------------------------------------------------------------------------------
def search_file_name_in_root(file_name):
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

    for file in file_list:
        if file['title'] == file_name:
            return file['id']

    return file_list[0]['id']  # Обробити виключення: якщо файл не знайдено


def search_file_name_in_subfolders(file_name):
    root_lists = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

    for files in root_lists:
        list_files = drive.ListFile({'q': f"'{files['id']}' in parents and trashed=false"}).GetList()
        if list_files['title'] == file_name:
            return list_files['id']

    return root_lists[0]['id']  # Обробити виключення: якщо файл не знайдено


# ------------------------------------------------------------------------------------------------------------------

@dp.message_handler(commands="add_file", state=None)
async def add_file_message(message: types.Message):
    await message.answer("Надішліть файл для завантаженна на Google drive:")
    await FileState.fsm_add.set()


@dp.message_handler(content_types=['document'], state=FileState.fsm_add)
async def add_photo(message: types.Message, state: FSMContext):
    folder_id = 'root'
    file_name = 'Faye.jpg'
    file_path = 'D:/' + file_name
    await message.photo[-1].download(destination_file=file_path)
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    os.remove(file_path)
    await state.finish()


# ------------------------------------------------------------------------------------------------------------------
@dp.message_handler(commands="create_folder", state=None)  # функція створення папки
async def process_create_folder(message: types.Message):
    await message.answer(f"Введіть назву папки:")
    await FileState.fsm_create_folder.set()  # стан очікування назви створеної папки


@dp.message_handler(state=FileState.fsm_create_folder)  # функція стану очікування назви створеної папки
async def create_folder(message: types.Message, state: FSMContext):
    name_folder = message.text
    async with state.proxy() as data:
        data['ref1'] = name_folder
    await message.answer(
        f"Введіть назву папки у якій хочете створити папку, або напищіть root,щоб створення відбулося в корінній папці:")
    await FileState.fsm_choice_create_folder.set()


@dp.message_handler(state=FileState.fsm_choice_create_folder)  # функція стану очікування назви створеної папки
async def create_folder(message: types.Message, state: FSMContext):
    name_path_to_save_folder = message.text

    async with state.proxy() as data:
        name_folder = data['ref1']

    file_metadata = {
        'name': name_folder,  # назва папки (вводится через телеграм)
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [search_file_name_in_root(name_path_to_save_folder) if name_path_to_save_folder != 'root' else 'root']
    }
    service.files().create(body=file_metadata).execute()  # створення нової пустої папки
    await message.answer(f"Папка успішно створена.")
    await state.finish()


# ------------------------------------------------------------------------------------------------------------------
@dp.message_handler(commands="delete_folder", state=None)  # функція видалення папки або файлу по id
async def file_delete_message(message: types.Message):
    await message.answer(f"Введите id папки которую хотите удалить:")
    await FileState.fsm_delete.set()


@dp.message_handler(state=FileState.fsm_delete)
async def file_delete(message: types.Message, state: FSMContext):
    file_id = search_file_name_in_root(message.text)  #
    service.files().delete(fileId=file_id).execute()  # видалення папки або файлу по id

    await message.answer(f"Папка успішно видалена.")
    await state.finish()


# ------------------------------------------------------------------------------------------------------------------
@dp.message_handler(commands="download", state=None)  # функція завантаження, (функціонал у розробці)
async def download_file(message: types.Message):
    await message.answer(f"Введіть назву файлу, який бажаете завантажити:")
    await FileState.fsm_download.set()


@dp.message_handler(state=FileState.fsm_download)
async def download(message: types.Message, state: FSMContext):
    file_name = message.text
    file_id = search_file_name_in_subfolders(file_name)

    request = service.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)

    done = False

    while not done:
        status, done = downloader.next_chunk()
        await message.answer(f'Download progress...')
    fh.seek(0)
    with open(os.path.join('D:/', file_name), 'wb') as f:
        f.write(fh.read())
        f.close()

    await message.reply_document(open(os.path.join('D:/', file_name), 'rb'))
    await message.answer(f"Файл завантажен.")
    path = os.path.join('D:/', file_name)
    os.remove(path)
    await state.finish()


# ------------------------------------------------------------------------------------------------------------------
@dp.message_handler(commands="info", state=None)  # функція завантаження, (функціонал у розробці)
async def info_file(message: types.Message):
    await message.answer(
        "Введите имя папки о содержании которой хотите получить информацию, если хотите осмотреть только коренную папку введите root")
    await FileState.fsm_info.set()


@dp.message_handler(state=FileState.fsm_info)
async def download_file(message: types.Message, state: FSMContext):
    gd_folder_name = message.text
    if gd_folder_name != 'root':
        gd_folder_path = search_file_name_in_root(gd_folder_name)
    else:
        gd_folder_path = "root"

    fileList = drive.ListFile({'q': f"'{gd_folder_path}' in parents and trashed=false"}).GetList()
    for file in fileList:
        await message.answer('Title: %s,\nID: %s' % (file['title'], file['id']))
        # Get the folder ID that you want
    await state.finish()


# ------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
