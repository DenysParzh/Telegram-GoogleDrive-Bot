import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from aiogram.fsm.storage.memory import MemoryStorage

from gdrive.google import create_service
from utils.constants import CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES

load_dotenv()
storage = MemoryStorage()
bot = Bot(token=os.environ["TOKEN"])
dp = Dispatcher(storage=storage)

google_auth = GoogleAuth()
drive = GoogleDrive(google_auth)
service = None #create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
