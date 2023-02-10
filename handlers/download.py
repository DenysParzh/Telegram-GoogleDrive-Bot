import os

from aiogram import types, Router, F
from aiogram.filters import Command

from loader import bot
from utils.callbackdata import DownloadFile
from utils.constants import MIME_TYPE_FOLDER
from keyboards.inline import create_inline_button
from gdrive.scripts import search_file_id, download

router = Router()


# функція завантаження
@router.message(Command(commands="download"))
async def download_message(message: types.Message):
    await message.answer(
        "Папки:",
        reply_markup=create_inline_button(folder_id="root")
    )


@router.callback_query(DownloadFile.filter(F.mime_type == MIME_TYPE_FOLDER))
async def send_value(query: types.CallbackQuery, callback_data: DownloadFile):
    folder_name = callback_data.file_name
    folder_id = search_file_id(folder_name)

    await query.message.answer(
        f"Папки {folder_name}:",
        reply_markup=create_inline_button(
            folder_id='root' if folder_id is None else folder_id
        )
    )


@router.callback_query(DownloadFile.filter(F.mime_type == "file"))
async def send_value(query: types.CallbackQuery, callback_data: DownloadFile):
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
