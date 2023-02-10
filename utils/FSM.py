from aiogram.fsm.state import StatesGroup, State


class FileState(StatesGroup):
    fsm_upload = State()
    fsm_upload_folder_name = State()
    fsm_info = State()
    fsm_create_folder = State()
    fsm_choice_create_folder = State()
    fsm_delete = State()
    fsm_download = State()
