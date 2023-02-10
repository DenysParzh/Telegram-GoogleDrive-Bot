from aiogram.filters.callback_data import CallbackData


class DownloadFile(CallbackData, prefix="file"):
    file_name: str
    mime_type: str


class Fileinfo(CallbackData, prefix="info"):
    name: str
