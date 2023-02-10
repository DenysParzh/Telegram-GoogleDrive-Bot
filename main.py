import asyncio
import logging

from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import bot, dp
import handlers

logging.basicConfig(level=logging.INFO)


@dp.message(Command(commands='stop'))
async def stop_states(message: types.Message, state: FSMContext):
    await state.clear()


async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        dp.include_router(handlers.start.router)
        dp.include_router(handlers.login.router)
        dp.include_router(handlers.upload.router)
        dp.include_router(handlers.download.router)
        dp.include_router(handlers.create.router)
        dp.include_router(handlers.delete.router)
        dp.include_router(handlers.folders_info.router)
        await dp.start_polling(bot)
    except Exception as e:
        print(e)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
