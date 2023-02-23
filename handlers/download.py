import os

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import FSInputFile

from loader import bot
from gdrive.google import GoogleDrive
from utils.callbackdata import DownloadFile
from keyboards.inline import create_inline_button

router = Router()


# функція завантаження
@router.message(Command(commands="download"))
async def download_message(message: types.Message):
    await message.answer(
        "Папки:",
        reply_markup=create_inline_button(folder_id="root",
                                          user_id=message.from_user.id)
    )


@router.callback_query(DownloadFile.filter(F.mime_type == GoogleDrive.MIME_TYPE_FOLDER))
async def send_value(query: types.CallbackQuery, callback_data: DownloadFile):
    user_id = query.from_user.id
    folder_name = callback_data.file_name
    folder_id = GoogleDrive(user_id).search_id(folder_name)

    await query.message.answer(
        f"Папки {folder_name}:",
        reply_markup=create_inline_button(
            folder_id='root' if folder_id is None else folder_id,
            user_id=user_id
        )
    )


@router.callback_query(DownloadFile.filter(F.mime_type == "file"))
async def send_value(query: types.CallbackQuery, callback_data: DownloadFile):
    user_id = query.from_user.id
    file_name = callback_data.file_name
    abs_path = GoogleDrive(user_id).download_file(file_name)

    downloaded_file = FSInputFile(abs_path, filename=file_name)
    await bot.send_document(query.message.chat.id, document=downloaded_file)
    os.remove(abs_path)


@router.callback_query(F.data == "root")
async def send_value(query: types.CallbackQuery):
    await query.message.answer(
        "Папки:",
        reply_markup=create_inline_button(user_id=query.from_user.id)
    )
