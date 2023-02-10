import os

from aiogram import Bot, Dispatcher
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from aiogram.fsm.storage.memory import MemoryStorage

from gdrive.google import create_service
from utils.constants import CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES

storage = MemoryStorage()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(storage=storage)

google_auth = GoogleAuth()
google_auth.LoadCredentialsFile("mycreds.txt")
google_auth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(google_auth)
service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
