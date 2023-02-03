from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import os

import markups

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(f"Привет {message.from_user.first_name}!\nНапиши мне что-нибудь!")


@dp.message_handler(commands=['commands'])
async def process_start_command(message: types.Message):
    await message.answer(f"Привет!\nНапиши мне 😘😘😘😘что-нибудь!")


@dp.message_handler()
async def echo_message(msg: types.Message):
    if msg.text == "Den":
        await msg.answer(f"God!")
    elif msg.text == "Andrew":
        await msg.answer(f"-_-!")
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
