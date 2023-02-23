import os

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import bot
from utils.FSM import FileState
from keyboards.reply import button_stop
from gdrive.google import GoogleDrive
from config import CACHE_FOLDER_NAME

router = Router()


async def download_tg_file(file_name: str, file_id: str) -> str:
    abs_path = f"{CACHE_FOLDER_NAME}\\{file_name}"
    await bot.download(file_id, abs_path)
    return abs_path


@router.message(Command(commands='upload'))
async def upload_message(message: types.Message, state: FSMContext):
    await message.answer("⬇️ Введіть назву папки на Google Drive ⬇️", reply_markup=button_stop)
    await state.set_state(FileState.fsm_upload_folder_name)


@router.message(FileState.fsm_upload_folder_name)
async def upload_folder_name(message: types.Message, state: FSMContext):
    file_name = message.text
    user_id = message.from_user.id
    user_data = GoogleDrive(user_id)
    folder_id = user_data.search_id(file_name)

    await state.update_data(folder_id=folder_id, user_data=user_data)
    await message.answer("Якщо хочете припинити завантажувати файли, натисніть stop "
                         "\n⬇️ Надішліть файл(и) для завантаження ⬇️")  # reply_markup=button_stop

    await state.set_state(FileState.fsm_upload)


@router.message(FileState.fsm_upload, F.document)
async def upload_document(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]
    user_data = data["user_data"]

    file_name = message.document.file_name
    file_id = message.document.file_id
    mime_type = message.document.mime_type

    abs_path = await download_tg_file(file_name, file_id)
    user_data.upload_file(file_name, mime_type,
                          folder_id, abs_path)
    os.remove(abs_path)


@router.message(FileState.fsm_upload, F.photo)
async def upload_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]
    user_data = data["user_data"]

    photo_id = message.photo[-1].file_id
    photo_info = await bot.get_file(photo_id)
    photo_name = photo_info.file_path.split('/')[-1]
    mime_type = f'image/{photo_name.split(".")[-1]}'

    abs_path = await download_tg_file(photo_name, photo_id)
    user_data.upload_file(photo_name, mime_type,
                          folder_id, abs_path)
    os.remove(abs_path)


@router.message(FileState.fsm_upload, F.video)
async def upload_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]
    user_data = data["user_data"]

    video_name = message.video.file_name
    mime_type = message.video.mime_type
    video_id = message.video.file_id

    abs_path = await download_tg_file(video_name, video_id)
    user_data.upload_file(video_name, mime_type,
                          folder_id, abs_path)
    os.remove(abs_path)


@router.message(FileState.fsm_upload, F.voice)
async def upload_voice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]
    user_data = data["user_data"]

    voice_id = message.voice.file_id
    voice_info = await bot.get_file(voice_id)
    voice_name = voice_info.file_path.split('/')[-1]
    mime_type = message.voice.mime_type

    abs_path = await download_tg_file(voice_name, voice_id)
    user_data.upload_file(voice_name, mime_type,
                          folder_id, abs_path)
    os.remove(abs_path)


@router.message(FileState.fsm_upload, F.audio)
async def upload_audio(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]
    user_data = data["user_data"]

    audio_name = message.audio.file_name
    mime_type = message.audio.mime_type
    audio_id = message.audio.file_id

    abs_path = await download_tg_file(audio_name, audio_id)
    user_data.upload_file(audio_name, mime_type,
                          folder_id, abs_path)
    os.remove(abs_path)


@router.message(FileState.fsm_upload, F.video_note)
async def upload_video_node(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]
    user_data = data["user_data"]

    video_note_id = message.video_note.file_id
    video_note_info = await bot.get_file(video_note_id)
    video_note_name = video_note_info.file_path.split('/')[-1]
    mime_type = "video/mp4"

    abs_path = await download_tg_file(video_note_name, video_note_id)
    user_data.upload_file(video_note_name, mime_type,
                          folder_id, abs_path)
    os.remove(abs_path)


@router.message(FileState.fsm_upload, F.animation)
async def upload_animation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]
    user_data = data["user_data"]

    animation_name = message.animation.file_name
    animation_id = message.animation.file_id
    mime_type = message.animation.mime_type

    abs_path = await download_tg_file(animation_name, animation_id)
    user_data.upload_file(animation_name, mime_type,
                          folder_id, abs_path)
    os.remove(abs_path)
