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

google_auth.LoadCredentialsFile("mycreds.txt")
if google_auth.credentials is None:
    google_auth.LocalWebserverAuth()
elif google_auth.access_token_expired:
    google_auth.Refresh()
else:
    google_auth.Authorize()
google_auth.SaveCredentialsFile("mycreds.txt")

# client_secrets.json need to be in the same directory as the script
drive = GoogleDrive(google_auth)
