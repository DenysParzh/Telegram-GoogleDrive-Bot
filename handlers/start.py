import json

from aiogram import types, Router
from aiogram.filters import Command
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from utils.constants import SCOPES, CLIENT_SECRET_FILE

router = Router()
G_DRIVE_CLIENT_ID = "223423955182-4rb2o4lutp5o180acs0qo7qgfh2b5166.apps.googleusercontent.com"
CLIENT_SECRET_DESK = "client_secret_test.json"
REDIRECT_URI = 'http://localhost/users/auth/google_oauth2/callback'
CALLBACK_URL = 'http://localhost:8080/oauth2callback'
REDIRECT_URI_LOVE = 'urn:ietf:wg:oauth:2.0:oob'

@router.message(Command(commands='start'))
async def process_start_command(message: types.Message):
    try:
        flow = InstalledAppFlow.from_client_config(client_config=json.loads(open(CLIENT_SECRET_DESK).read()),
                                                   scopes=SCOPES,
                                                   redirect_uri=CALLBACK_URL)

        auth_url = flow.run_local_server()
        await message.answer(f"{auth_url}")




    # service = build('drive', 'v3', credentials=creds)

    # result_file = service.files().list(q="name='root'").execute()

    # await message.answer(f"{results}")
    except Exception as ex:
        print(f"Error: {ex}")
