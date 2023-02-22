from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from gdrive.sql_helper.gdrive_database import set_creds, get_creds
from utils.constants import SCOPES
from utils.FSM import FileState

router = Router()

CLIENT_SECRET_DESK = "client_secret_test.json"
CALLBACK_URL = 'http://localhost:8080/oauth2callback'
AUTH_URL = '<a href ="{}">Vist This Url</a>'

flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=CLIENT_SECRET_DESK,
                                                 scopes=SCOPES,
                                                 redirect_uri=CALLBACK_URL)


@router.message(Command(commands='login'))
async def user_login(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    creds = get_creds(user_id)

    try:
        if creds is not None:

            creds.refresh(Request())
            await set_creds(user_id, creds)

            await message.answer("✅Ви авторизовані✅")
        else:
            auth_url, _ = flow.authorization_url(prompt='consent', access_type="offline")
            AUTH = AUTH_URL.format(auth_url)

            await message.answer(AUTH, parse_mode='HTML')
            await message.answer('⬇️Скопіюйте посилання та вставте його⬇️')

            await state.set_state(FileState.fsm_auth)

    except Exception as ex:
        print(f"Error: {ex}")


@router.message(FileState.fsm_auth)
async def process_login(message: types.Message):
    try:
        auth_url = message.text
        user_id = message.from_user.id

        start = auth_url.find("4/")
        end = auth_url.find("&scope")
        auth_code = auth_url[start:end]

        flow.fetch_token(code=auth_code)
        cred = flow.credentials

        await set_creds(user_id, cred)
        await message.answer("✅Авторизація пройдена успішно✅")

    except Exception as ex:
        await message.answer("Помилка Авторизації")
        print(f"Error: {ex}")
