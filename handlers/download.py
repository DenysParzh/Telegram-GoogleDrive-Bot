import os
import io

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from googleapiclient.http import MediaIoBaseDownload
from aiogram.types import FSInputFile

from FSM import FileState
from keyboards.reply import button_stop
from loader import bot, service
from constants import CACHE_FOLDER_NAME, MIME_TYPE_FOLDER
from gdrive_utils.scripts import search_file_id, create_inline_button, FileInfo

router = Router()


# функція завантаження
@router.message(Command(commands="download"))
async def download_message(message: types.Message):
    await message.answer(
        "Папки:",
        reply_markup=create_inline_button(folder_id="root")
    )


def download(file_name):
    try:
        file_id = search_file_id(file_name)
        abs_path = f"{CACHE_FOLDER_NAME}\\{file_name}"

        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(fd=file, request=request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        file.seek(0)
        with open(abs_path, "wb") as new_file:
            new_file.write(file.read())
            file.close()

        cache_file = FSInputFile(abs_path, filename=file_name)

        return cache_file, abs_path

    except Exception as error:
        print(F'{error}')


@router.callback_query(FileInfo.filter(F.mime_type == MIME_TYPE_FOLDER))
async def send_value(query: types.CallbackQuery, callback_data: FileInfo):

    folder_name = callback_data.file_name
    folder_id = search_file_id(folder_name)

    await query.message.answer(
        f"Папки {folder_name}:",
        reply_markup=create_inline_button(
            folder_id='root' if folder_id is None else folder_id
        )
    )


@router.callback_query(FileInfo.filter(F.mime_type == "file"))
async def send_value(query: types.CallbackQuery, callback_data: FileInfo):
    file_name = callback_data.file_name
    downloaded_file, abs_path = download(file_name)
    await bot.send_document(query.message.chat.id, document=downloaded_file)
    os.remove(abs_path)


@router.callback_query(F.data == "root")
async def send_value(query: types.CallbackQuery):
    await query.message.answer(
        "Папки:",
        reply_markup=create_inline_button(folder_id="root")
    )
