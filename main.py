import asyncio
import logging

from aiogram import types, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext

import handlers
from loader import bot, dp

logging.basicConfig(level=logging.INFO)

from loader import service, drive
from gdrive_utils.scripts import search_file_id

from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import CallbackQuery


@dp.message(Command(commands='stop'))
async def stop_states(message: types.Message, state: FSMContext):
    await state.clear()


# class CallBackFolders(CallbackData, prefix="Folder"):
#     name: str

#
@dp.message(Command(commands='folders_info'))
async def folders_info(message: types.Message, folder_id='root'):
    response = service.files().list(q=f"parents='{folder_id}'").execute()
    builder = InlineKeyboardBuilder()
    await message.answer("Download...")
    i = 0
    while i < len(response["files"]):
        response = service.files().list(q=f"parents='{folder_id}'").execute()
        builder.button(text=response["files"][i]['name'],
                       callback_data="root")
        i = i + 1

    builder.button(text='Назад',  callback_data="root")

    builder.adjust(3)
    await message.answer(
        "Папки:",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(CallbackData.filter())
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str(1))
    await callback.answer()


async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        dp.include_router(handlers.start.router)
        dp.include_router(handlers.login.router)
        dp.include_router(handlers.upload.router)
        dp.include_router(handlers.download.router)
        dp.include_router(handlers.create.router)
        dp.include_router(handlers.delete.router)
        await dp.start_polling(bot)
    except Exception as e:
        print(e)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
