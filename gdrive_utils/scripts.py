import os

from aiogram.utils.keyboard import InlineKeyboardBuilder
from googleapiclient.http import MediaFileUpload
from constants import CACHE_FOLDER_NAME
from loader import bot, service


def search_file_id(file_name):
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


def create_inline_button(folder_id="root"):
    response = service.files().list(q=f"parents='{folder_id}'").execute()
    builder = InlineKeyboardBuilder()

    for index, value in enumerate(response["files"]):
        builder.button(text=response["files"][index]['name'],
                       callback_data=response["files"][index]['name'])

    builder.button(text='Назад', callback_data="root")

    builder.adjust(3)
    return builder.as_markup()
