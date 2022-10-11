from fastapi import APIRouter, UploadFile, File
from fastapi_sqlalchemy import db

from calendar_backend.exceptions import ObjectNotFound
from calendar_backend.methods import utils
from calendar_backend.models.db import ApproveStatuses
from calendar_backend.models.db import Photo as DbPhoto
from calendar_backend.routes.models import (
    Photo,
    LecturerPhotos,
)

lecturer_photo_router = APIRouter(prefix="/timetable/lecturer/{lecturer_id}", tags=["Lecturer: Photo"])


@lecturer_photo_router.post("/photo", response_model=Photo)
async def upload_photo(lecturer_id: int, photo: UploadFile = File(...)) -> Photo:
    """Загрузить фотографию преподавателя из локального файла
    
    Пример загрузки файла на питоне
    ```python
    lecturer_id = 123
    root = 'https://timetable.api.test.profcomff.com'
    
    with open('./x.png', 'rb') as f:
        data = f.read()
    requests.post(url=f'{root}/timetable/lecturer/{lecturer_id}/photo', files={"photo": data})
    ```
    """
    return Photo.from_orm(await utils.upload_lecturer_photo(lecturer_id, db.session, file=photo))


@lecturer_photo_router.get("/photo", response_model=LecturerPhotos)
async def get_lecturer_photos(lecturer_id: int, limit: int = 10, offset: int = 0) -> LecturerPhotos:
    res = DbPhoto.get_all(session=db.session).filter(DbPhoto.lecturer_id == lecturer_id)
    if limit:
        cnt, res = res.count(), res.offset(offset).limit(limit).all()
    else:
        cnt, res = res.count(), res.offset(offset).all()
    return LecturerPhotos(**{"items": [row.link for row in res], "limit": limit, "offset": offset, "total": cnt})


@lecturer_photo_router.delete("/photo/{id}", response_model=None)
async def delete_photo(id: int, lecturer_id: int) -> None:
    photo = DbPhoto.get(id, only_approved=False, session=db.session)
    if photo.lecturer_id != lecturer_id:
        raise ObjectNotFound(DbPhoto, id)
    return DbPhoto.delete(id=id, session=db.session)

@lecturer_photo_router.get("/photo/{id}", response_model=Photo)
async def get_photo(id: int, lecturer_id: int) -> Photo:
    photo = DbPhoto.get(id, session=db.session)
    if photo.lecturer_id != lecturer_id or photo.approve_status != ApproveStatuses.APPROVED:
        raise ObjectNotFound(DbPhoto, id)
    return Photo.from_orm(photo)
