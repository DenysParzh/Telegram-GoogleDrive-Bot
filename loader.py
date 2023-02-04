from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

storage = MemoryStorage()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)
google_auth = GoogleAuth()
google_auth.LocalWebserverAuth()  # client_secrets.json need to be in the same directory as the script
drive = GoogleDrive(google_auth)
