from aiogram import types, Router
from aiogram.filters import Command

router = Router()


@router.message(Command(commands='start'))
async def process_start_command(message: types.Message):
    await message.answer(f"Привет {message.from_user.first_name}!\nНапиши мне что-нибудь!")

