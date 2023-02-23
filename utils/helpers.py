from gdrive.google import GoogleDrive


def check_folder(mime_type: str) -> str:
    return "file" if mime_type != GoogleDrive.MIME_TYPE_FOLDER else mime_type
