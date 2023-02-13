from aiogram import types, Router
from aiogram.filters import Command

from loader import google_auth, drive


router = Router()

AUTH_URL = '<a href ="{}">Vist This Url</a>'


@router.message(Command(commands='login'))
async def user_login(message: types.Message) -> None:
    try:

        auth_url = google_auth.GetAuthUrl()
        AUTH = AUTH_URL.format(auth_url)
        await message.answer(AUTH, parse_mode='HTML')

    except Exception as ex_info:
        print(f"Інформація про помилку: {ex_info}")
