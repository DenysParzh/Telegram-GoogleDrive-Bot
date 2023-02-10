import os

from aiogram.utils.keyboard import InlineKeyboardBuilder, CallbackData
from googleapiclient.http import MediaFileUpload
from constants import CACHE_FOLDER_NAME, MIME_TYPE_FOLDER
from loader import bot, service
import pprint

pp = pprint.PrettyPrinter(indent=4)


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


class DownloadFile(CallbackData, prefix="file"):
    file_name: str
    mime_type: str


class Fileinfo(CallbackData, prefix="info"):
    name: str


def validate_mime_type(mime_type: str) -> str:
    return "file" if mime_type != MIME_TYPE_FOLDER else mime_type


def create_inline_button(folder_id="root"):
    response = service.files().list(q=f"parents='{folder_id}'").execute()
    builder = InlineKeyboardBuilder()

    for file in response["files"]:
        builder.button(text=file['name'],
                       callback_data=DownloadFile(file_name=file["name"],
                                                  mime_type=validate_mime_type(file["mimeType"])).pack())

    builder.button(text='Назад', callback_data="root")

    builder.adjust(3)
    return builder.as_markup()


def create_inline_button_for_info(folder_id="root"):
    response = service.files().list(q=f"parents='{folder_id}'").execute()
    builder = InlineKeyboardBuilder()

    for file in response["files"]:
        builder.button(text=file['name'],
                       callback_data=Fileinfo(name=file["name"]).pack())

    builder.button(text='Назад', callback_data=Fileinfo(name="back").pack())

    builder.adjust(3)
    return builder.as_markup()
