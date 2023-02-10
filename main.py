import asyncio
import logging

from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import handlers
from loader import bot, dp

logging.basicConfig(level=logging.INFO)

from loader import service, drive

from aiogram.utils.keyboard import InlineKeyboardBuilder

from gdrive_utils.scripts import search_file_id, create_inline_button


@dp.message(Command(commands='stop'))
async def stop_states(message: types.Message, state: FSMContext):
    await state.clear()




@dp.message(Command(commands='folders_info'))
async def folders_info(message: types.Message):
    await message.answer(
        "Папки:",
        reply_markup=create_inline_button(folder_id="root")
    )


@dp.callback_query()
async def send_value(call: types.CallbackQuery):
    folder_id = search_file_id(call.data)

    await call.message.answer(
        f"Папки {call.data}:",
        reply_markup=create_inline_button(folder_id='root' if folder_id is None else folder_id)
    )





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
