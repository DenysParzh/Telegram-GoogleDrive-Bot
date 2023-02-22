from aiogram import types, Router
from aiogram.filters import Command

router = Router()


@router.message(Command(commands='start'))
async def process_start_command(message: types.Message):
    try:
        await message.answer(f"Hi {message.from_user.username}")
    except Exception as ex:
        print(f"Error: {ex}")
