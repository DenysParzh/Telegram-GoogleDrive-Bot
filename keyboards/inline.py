from aiogram.utils.keyboard import InlineKeyboardBuilder

from loader import service
from utils.helpers import check_folder
from utils.callbackdata import DownloadFile, Fileinfo


def create_inline_button(folder_id="root"):
    response = service.files().list(q=f"parents='{folder_id}'").execute()
    builder = InlineKeyboardBuilder()

    for file in response["files"]:
        builder.button(text=file['name'],
                       callback_data=DownloadFile(file_name=file["name"],
                                                  mime_type=check_folder(file["mimeType"])).pack())

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