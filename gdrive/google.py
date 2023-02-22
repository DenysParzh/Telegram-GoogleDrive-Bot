import os
import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from gdrive.sql_helper import gdrive_database
from utils.constants import CACHE_FOLDER_NAME


class GoogleDrive:
    __API_VERSION: str = 'v3'
    __API_NAME: str = 'drive'
    __G_DRIVE_MIME_TYPE_FOLDER: str = "application/vnd.google-apps.folder"
    __G_DRIVE_BASE_DOWNLOAD_URL: str = "https://drive.google.com/uc?id={}&export=download"

    def __init__(self, user_id):
        self.__service = self.authorize(gdrive_database.get_creds(user_id))

    @classmethod
    def authorize(cls, creds):
        if creds is not None:
            return build(cls.__API_NAME, cls.__API_VERSION, credentials=creds)
        return None

    @classmethod
    def create_file_metadata(cls, file_name, mime_type, folder_id):
        return {
            'name': file_name,
            'mimeType': mime_type,
            'parents': ['root' if folder_id is None else folder_id]
        }

    def search_file_id(self, file_name):
        try:
            result_file = self.__service.files().list(q=f"name='{file_name}'").execute()
            if len(result_file["files"] > 0):
                return result_file["files"][0]["id"]
            else:
                logging.error(f"Could not find file '{file_name}'")
        except HttpError as error:
            logging.error(f"Error searching file '{file_name}': {error}")
        finally:
            return None

    def upload_file(self, file_name, mime_type, folder_id, abs_path):
        file_metadata = self.create_file_metadata(file_name, mime_type, folder_id)

        try:
            media = MediaFileUpload(filename=abs_path,
                                    mimetype=mime_type,
                                    resumable=True)
            uploaded_file = self.__service.files().create(body=file_metadata,
                                                          media_body=media,
                                                          fields='id').execute()

            logging.info(f'File {file_name} uploaded to Google Drive with ID: {uploaded_file.get("id")}')

        except HttpError as error:
            logging.error(f'An error occurred while uploading the file {file_name}: {error}')
        except FileNotFoundError as error:
            logging.error(f"Could not find the file {abs_path}: {error}")
        except Exception as error:
            logging.error(f'An error occurred while uploading the file {file_name}: {error}')
