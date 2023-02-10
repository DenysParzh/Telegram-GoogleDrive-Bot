from aiogram import types, Router, F
from aiogram.filters import Command
from gdrive_utils.scripts import search_file_id, Fileinfo, create_inline_button_for_info


router = Router()


@router.message(Command(commands='folders_info'))
async def folders_info(message: types.Message):
    await message.answer(
        "Папки:",
        reply_markup=create_inline_button_for_info(folder_id="root")
    )


@router.callback_query(Fileinfo.filter())
async def send_value(call: types.CallbackQuery, callback_data: Fileinfo):

    folder_id = search_file_id(callback_data.name)
    await call.message.answer(
        f"Папки {callback_data.name}:",
        reply_markup=create_inline_button_for_info(folder_id='root' if folder_id is None else folder_id)
    )
