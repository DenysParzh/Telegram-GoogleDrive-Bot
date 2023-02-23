import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
TOKEN=os.environ["TOKEN"]
SCOPES =os.environ["SCOPES"]
CLIENT_SECRET_FILE =os.environ["CLIENT_SECRET_FILE"]
CACHE_FOLDER_NAME = os.environ["CACHE_FOLDER_NAME "]
