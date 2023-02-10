import os

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.reply import button_stop
from loader import bot
from FSM import FileState
from constants import CACHE_FOLDER_NAME
from gdrive_utils.scripts import search_file_id, upload_file

router = Router()


@router.message(Command(commands='upload'))
async def upload_message(message: types.Message, state: FSMContext):
    await message.answer("⬇️ Введіть назву папки на Google Drive ⬇️", reply_markup=button_stop)
    await state.set_state(FileState.fsm_upload_folder_name)


@router.message(FileState.fsm_upload_folder_name)
async def upload_folder_name(message: types.Message, state: FSMContext):
    folder_id = search_file_id(message.text)
    await state.update_data(folder_id=folder_id)
    await message.answer("⬇️ Надішліть файл/файли для завантаження ⬇️")
    await message.answer("Якщо хочете припинити завантажувати файли введіть stop"
                         )  # reply_markup=button_stop
    await state.set_state(FileState.fsm_upload)


@router.message(FileState.fsm_upload, F.document)
async def upload_document(message: types.Message, state: FSMContext):
    if not os.path.exists(CACHE_FOLDER_NAME):
        os.mkdir(CACHE_FOLDER_NAME)

    data = await state.get_data()
    folder_id = data["folder_id"]

    file_name = message.document.file_name
    file_id = message.document.file_id
    mime_type = message.document.mime_type
    await upload_file(file_name, mime_type, folder_id, file_id)


@router.message(FileState.fsm_upload, F.photo)
async def upload_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    photo_id = message.photo[-1].file_id
    photo_info = await bot.get_file(photo_id)
    photo_name = photo_info.file_path.split('/')[-1]
    mime_type = f'image/{photo_name.split(".")[-1]}'

    await upload_file(photo_name, mime_type, folder_id, photo_id)


@router.message(FileState.fsm_upload, F.video)
async def upload_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    video_name = message.video.file_name
    mime_type = message.video.mime_type
    video_id = message.video.file_id

    await upload_file(video_name, mime_type, folder_id, video_id)


@router.message(FileState.fsm_upload, F.voice)
async def upload_voice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    voice_id = message.voice.file_id
    voice_info = await bot.get_file(voice_id)
    voice_name = voice_info.file_path.split('/')[-1]

    voice_id = message.voice.file_id
    mime_type = message.voice.mime_type

    await upload_file(voice_name, mime_type, folder_id, voice_id)


@router.message(FileState.fsm_upload, F.audio)
async def upload_audio(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    audio_name = message.audio.file_name
    mime_type = message.audio.mime_type
    audio_id = message.audio.file_id

    await upload_file(audio_name, mime_type, folder_id, audio_id)


@router.message(FileState.fsm_upload, F.video_note)
async def upload_video_node(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    video_note_id = message.video_note.file_id
    video_note_info = await bot.get_file(video_note_id)
    video_note_name = video_note_info.file_path.split('/')[-1]
    mime_type = "video/mp4"

    await upload_file(video_note_name, mime_type, folder_id, video_note_id)


@router.message(FileState.fsm_upload, F.animation)
async def upload_animation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data["folder_id"]

    animation_name = message.animation.file_name
    animation_id = message.animation.file_id
    mime_type = message.animation.mime_type

    await upload_file(animation_name, mime_type, folder_id, animation_id)
