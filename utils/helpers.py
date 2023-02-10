from utils.constants import MIME_TYPE_FOLDER


def check_folder(mime_type: str) -> str:
    return "file" if mime_type != MIME_TYPE_FOLDER else mime_type
