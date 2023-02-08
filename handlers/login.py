from aiogram import types, Router
from aiogram.filters import Command

from loader import google_auth

router = Router()


@router.message(Command(commands='login'))
async def user_login(message: types.Message) -> None:
    try:

        google_auth.LocalWebserverAuth()

        await message.answer("Вы залогинились")
    except Exception as ex_info:
        print(f"Інформація про помилку: {ex_info}")
