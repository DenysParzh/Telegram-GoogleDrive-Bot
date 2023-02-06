from aiogram.fsm.state import StatesGroup, State


class FileState(StatesGroup):
    fsm_add = State()
    fsm_choice_add_folder = State()
    fsm_add_name_file = State()
    fsm_info = State()
    fsm_create_folder = State()
    fsm_choice_create_folder = State()
    fsm_delete = State()
    fsm_download = State()
