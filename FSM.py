from aiogram.dispatcher.filters.state import State, StatesGroup


class FileState(StatesGroup):
    fsm_photo = State()
    fsm_info = State()
    fsm_create_folder = State()
    fsm_delete = State()
    fsm_download = State()
