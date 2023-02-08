from aiogram.types import ReplyKeyboardRemove, KeyboardButtonPollType, ReplyKeyboardMarkup, KeyboardButton
from aiogram import types

kb = [
    [
        types.KeyboardButton(text="/stop 🛑"),
    ],
]
button_stop = types.ReplyKeyboardMarkup(
    keyboard=kb,
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Для зупинки натисніть кнопку /stop"
)
