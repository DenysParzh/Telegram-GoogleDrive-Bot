from aiogram import types, Router, F
from aiogram.filters import Command
from gdrive_utils.scripts import search_file_id, create_inline_button, FileInfo
from keyboards.reply import button_stop

from constants import MIME_TYPE_FOLDER

router = Router()


@router.message(Command(commands='folders_info'))
async def folders_info(message: types.Message):

    await message.answer(
        "Папки:",
        reply_markup=create_inline_button(folder_id="root")
    )


@router.callback_query()
async def send_value(call: types.CallbackQuery):
    folder_id = search_file_id(call.data)

    await call.message.answer(
        f"Папки {call.data}:",
        reply_markup=create_inline_button(
            folder_id='root' if folder_id is None else folder_id
        )
    )
