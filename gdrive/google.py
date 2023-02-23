import io
import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from config import CACHE_FOLDER_NAME
from gdrive.sql_helper import gdrive_database


class GoogleDrive:
    __API_VERSION: str = 'v3'
    __API_NAME: str = 'drive'
    MIME_TYPE_FOLDER: str = "application/vnd.google-apps.folder"
    BASE_DOWNLOAD_URL: str = "https://drive.google.com/uc?id={}&export=download"

    def __init__(self, user_id):
        self.__service = self.authorize(gdrive_database.get_creds(user_id))

    @classmethod
    def authorize(cls, creds):
        if creds is not None:
            return build(cls.__API_NAME, cls.__API_VERSION, credentials=creds)
        return None

    @classmethod
    def create_metadata(cls, name, mime_type, parent_id):
        return {
            'name': name,
            'mimeType': mime_type,
            'parents': ['root' if parent_id is None else parent_id]
        }

    def search_id(self, file_name):
        try:
            result_file = self.__service.files().list(q=f"name='{file_name}'").execute()
            return result_file["files"][0]["id"]
        except HttpError as error:
            logging.error(f"Error searching file '{file_name}': {error}")

    def get_files_list(self, folder_id):
        try:
            return self.__service.files().list(q=f"parents='{folder_id}'").execute()
        except HttpError as error:
            logging.error(f"Error get files list: {error}")

    def upload_file(self, file_name, mime_type, folder_id, abs_path):
        file_metadata = self.create_metadata(file_name, mime_type, folder_id)

        try:
            media = MediaFileUpload(filename=abs_path,
                                    mimetype=mime_type,
                                    resumable=True)
            uploaded_file = self.__service.files().create(body=file_metadata,
                                                          media_body=media,
                                                          fields='id').execute()

            logging.info(f'File {file_name} uploaded to Google Drive with ID: {uploaded_file.get("id")}')

        except HttpError as error:
            logging.error(f'An error occurred while uploading the file, {file_name}: {error}')
        except FileNotFoundError as error:
            logging.error(f"Could not find the file, {abs_path}: {error}")
        except Exception as error:
            logging.error(f'An error occurred while uploading the file, {file_name}: {error}')

    def create_folder(self, folder_name, parent_id):
        file_metadata = self.create_metadata(folder_name,
                                             self.MIME_TYPE_FOLDER,
                                             parent_id)
        try:
            self.__service.files().create(body=file_metadata).execute()
        except HttpError as error:
            logging.error(f'An http-error occurred while create folder, {folder_name}: {error}')
        except Exception as error:
            logging.error(f'An error occurred while create folder, {folder_name}: {error}')

    def delete_file(self, file_name):
        file_id = self.search_id(file_name)

        try:
            if file_id is not None:
                self.__service.files().delete(file_id=file_id).execute()
                return "Файл видалено!"
            return "Файл не знайдено!"
        except HttpError as error:
            logging.error(f'An http-error occurred while delete file, {file_name}: {error}')
        except Exception as error:
            logging.error(f'An error occurred while delete file, {file_name}: {error}')

    def download_file(self, file_name):
        try:
            file_id = self.search_id(file_name)
            abs_path = f"{CACHE_FOLDER_NAME}\\{file_name}"

            file = io.BytesIO()
            request = self.__service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(fd=file, request=request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            file.seek(0)
            with open(abs_path, "wb") as new_file:
                new_file.write(file.read())
            file.close()

            return abs_path

        except Exception as error:
            print(F'{error}')
