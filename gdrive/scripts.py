import os
import io

from aiogram.types import FSInputFile
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from loader import bot, service
from utils.constants import CACHE_FOLDER_NAME


def search_file_id(file_name): # перевірити на async
    try:
        result_file = service.files().list(q=f"name='{file_name}'").execute()
        return result_file["files"][0]["id"]
    except Exception as error:
        print(error)


async def upload_file(file_name, mimeType, folder_id, file_id):
    abs_path = f"{CACHE_FOLDER_NAME}\\{file_name}"
    file_metadata = {
        'name': f"{file_name}",
        'parents': ['root' if folder_id is None else folder_id]
    }

    await bot.download(file_id, abs_path)
    media = MediaFileUpload(abs_path, mimetype=mimeType)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    media.__del__()
    os.remove(abs_path)


def download(file_name):  # перевірити на async
    try:
        file_id = search_file_id(file_name)
        abs_path = f"{CACHE_FOLDER_NAME}\\{file_name}"

        file = io.BytesIO()
        request = service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(fd=file, request=request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        file.seek(0)
        with open(abs_path, "wb") as new_file:
            new_file.write(file.read())

        cache_file = FSInputFile(abs_path, filename=file_name)
        file.close()

        return cache_file, abs_path

    except Exception as error:
        print(F'{error}')
