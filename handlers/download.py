import os
import io

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from googleapiclient.http import MediaIoBaseDownload
from aiogram.types import FSInputFile

from FSM import FileState
from loader import bot, service
from constants import CACHE_FOLDER_NAME
from gdrive_utils.scripts import search_file_id

router = Router()


# функція завантаження
@router.message(Command(commands="download"))
async def download_message(message: types.Message, state: FSMContext):
    await message.answer(f"Введіть назву файлу, який бажаете завантажити:")
    await state.set_state(FileState.fsm_download)


@router.message(FileState.fsm_download)
async def download(message: types.Message, state: FSMContext):
    try:
        # await message.answer(reply_markup=button_stop)
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
