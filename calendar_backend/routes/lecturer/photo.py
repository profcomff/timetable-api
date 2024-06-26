from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi_sqlalchemy import db

from calendar_backend.exceptions import ObjectNotFound
from calendar_backend.methods.image import get_photo_webpath, upload_lecturer_photo
from calendar_backend.models.db import ApproveStatuses, Lecturer
from calendar_backend.models.db import Photo as DbPhoto
from calendar_backend.routes.models import LecturerPhotos, Photo
from calendar_backend.settings import get_settings


settings = get_settings()
router = APIRouter(prefix="/lecturer/{lecturer_id}", tags=["Lecturer: Photo"])


@router.post("/photo", response_model=Photo)
async def upload_photo(
    lecturer_id: int,
    photo: UploadFile = File(...),
    _=Depends(UnionAuth(scopes=["timetable.lecturer.photo.create"])),
) -> Photo:
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
    photo = await upload_lecturer_photo(lecturer_id, db.session, file=photo)
    db.session.commit()
    return Photo.model_validate(photo)


@router.get("/photo", response_model=LecturerPhotos)
async def get_lecturer_photos(lecturer_id: int, limit: int = 10, offset: int = 0) -> LecturerPhotos:
    if not Lecturer.get(id=lecturer_id, session=db.session):
        raise ObjectNotFound(Lecturer, lecturer_id)
    res = DbPhoto.get_all(session=db.session).filter(DbPhoto.lecturer_id == lecturer_id)
    if limit:
        cnt, res = res.count(), res.offset(offset).limit(limit).all()
    else:
        cnt, res = res.count(), res.offset(offset).all()
    return LecturerPhotos(
        items=[get_photo_webpath(row.link) for row in res],
        limit=limit,
        offset=offset,
        total=cnt,
    )


@router.delete("/photo/{id}", response_model=None)
async def delete_photo(
    id: int,
    lecturer_id: int,
    _=Depends(UnionAuth(scopes=["timetable.lecturer.photo.delete"])),
) -> None:
    photo = DbPhoto.get(id, only_approved=False, session=db.session)
    if photo.lecturer_id != lecturer_id:
        raise ObjectNotFound(DbPhoto, id)
    if photo.lecturer.avatar_id == photo.id:
        photo.lecturer.avatar_id = None
    DbPhoto.delete(id=id, session=db.session)
    db.session.commit()
    return None


@router.get("/photo/{id}", response_model=Photo)
async def get_photo(id: int, lecturer_id: int) -> Photo:
    if not Lecturer.get(id=lecturer_id, session=db.session):
        raise ObjectNotFound(Lecturer, lecturer_id)
    photo = DbPhoto.get(id, session=db.session)
    if photo.lecturer_id != lecturer_id or photo.approve_status != ApproveStatuses.APPROVED:
        raise ObjectNotFound(DbPhoto, id)
    return Photo.model_validate(photo)
