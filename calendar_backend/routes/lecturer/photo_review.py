from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as

from calendar_backend.exceptions import ObjectNotFound
from calendar_backend.models.db import ApproveStatuses, Lecturer
from calendar_backend.models.db import Photo as DbPhoto
from calendar_backend.routes.models import Action, Photo


# DEPRICATED TODO: Drop 2023-04-01
lecturer_photo_review_router = APIRouter(
    prefix="/timetable/lecturer/{lecturer_id}/photo", tags=["Lecturer: Photo Review"], deprecated=True
)
router = APIRouter(prefix="/lecturer/{lecturer_id}/photo", tags=["Lecturer: Photo Review"])


@lecturer_photo_review_router.get("/review/", response_model=list[Photo])  # DEPRICATED TODO: Drop 2023-04-01
@router.get("/review/", response_model=list[Photo])
async def get_unreviewed_photos(
    lecturer_id: int, _=Depends(UnionAuth(scopes=["timetable.lecturer.photo.review"]))
) -> list[Photo]:
    photos = (
        DbPhoto.get_all(session=db.session, only_approved=False)
        .filter(DbPhoto.lecturer_id == lecturer_id, DbPhoto.approve_status == ApproveStatuses.PENDING)
        .all()
    )
    return parse_obj_as(list[Photo], photos)


@lecturer_photo_review_router.post("/{id}/review/", response_model=Photo)  # DEPRICATED TODO: Drop 2023-04-01
@router.post("/{id}/review/", response_model=Photo)
async def review_photo(
    id: int,
    lecturer_id: int,
    action: Action,
    _=Depends(UnionAuth(scopes=["timetable.lecturer.photo.review"])),
) -> Photo:
    lecturer = Lecturer.get(lecturer_id, session=db.session)
    photo = DbPhoto.get(id, only_approved=False, session=db.session)
    if photo.lecturer_id != lecturer_id or photo.approve_status is not ApproveStatuses.PENDING:
        raise ObjectNotFound(DbPhoto, id)
    DbPhoto.update(photo.id, approve_status=action.action, session=db.session)
    if action == ApproveStatuses.DECLINED:
        DbPhoto.delete(photo.id, session=db.session)
    db.session.flush()
    lecturer.avatar_id = lecturer.last_photo.id if lecturer.last_photo else lecturer.avatar_id
    db.session.commit()
    return Photo.from_orm(photo)
