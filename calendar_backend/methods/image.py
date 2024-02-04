import asyncio
import os
import random
import string
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from io import BytesIO

import aiofiles
from fastapi import File, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from calendar_backend.models.db import ApproveStatuses, Lecturer, Photo
from calendar_backend.settings import get_settings


settings = get_settings()


async def upload_lecturer_photo(lecturer_id: int, session: Session, file: UploadFile = File(...)) -> Photo:
    """
    Uploads the lecturer's photo to the database
    """
    lecturer = Lecturer.get(lecturer_id, session=session)
    random_string = ''.join(random.choice(string.ascii_letters) for _ in range(32))
    ext = file.filename.split('.')[-1]
    if ext not in settings.SUPPORTED_FILE_EXTENSIONS:
        raise HTTPException(status_code=422, detail="Unsupported file extension")
    filename = f"{random_string}.{ext}"
    path = os.path.join(settings.STATIC_PATH, "photo", "lecturer", filename)
    async with aiofiles.open(path, 'wb') as out_file:
        content = await file.read()
        await async_image_process(content)
        await out_file.write(content)
        approve_status = ApproveStatuses.APPROVED if not settings.REQUIRE_REVIEW_PHOTOS else ApproveStatuses.PENDING
        photo = Photo(
            lecturer_id=lecturer_id,
            link=filename,
            approve_status=approve_status,
        )
        session.add(photo)
        session.flush()
        lecturer.avatar_id = lecturer.last_photo.id if lecturer.last_photo else lecturer.avatar_id
        session.flush()
    return photo


def process_image(image_bytes: bytes) -> None:
    """
    Checks the integrity of the image
    """
    with Image.open(BytesIO(image_bytes)) as image:
        try:
            image.verify()
        except SyntaxError:
            raise HTTPException(status_code=422, detail="Corrupted file")


thread_pool = ThreadPoolExecutor()


async def async_image_process(image_bytes: bytes) -> None:
    """
    Asynchronous image processing
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(thread_pool, partial(process_image, image_bytes))


def get_photo_webpath(file_path: str):
    """
    Returns the webpath of the file
    """
    file_path = file_path.removeprefix('/')
    root_path = settings.ROOT_PATH.removesuffix('/')
    return f"{root_path}/static/photo/lecturer/{file_path}"
