from aiogram import types, Router
from aiogram.filters import Command
from googleapiclient.discovery import build
from utils.FSM import FileState
from aiogram.fsm.context import FSMContext

router = Router()
# G_DRIVE_CLIENT_ID = "223423955182-4rb2o4lutp5o180acs0qo7qgfh2b5166.apps.googleusercontent.com"
CLIENT_SECRET_DESK = "client_secret_test.json"
# REDIRECT_URI = 'http://localhost/users/auth/google_oauth2/callback'
CALLBACK_URL = 'http://localhost:8080/oauth2callback'


# REDIRECT_URI_LOVE = 'urn:ietf:wg:oauth:2.0:oob'


@router.message(Command(commands='start'))
async def process_start_command(message: types.Message, state: FSMContext):
    try:
        await message.answer(f"Hi {message.from_user.username}")
    except Exception as ex:
        print(f"Error: {ex}")
