from typing import Literal

from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as

from calendar_backend.exceptions import ObjectNotFound
from calendar_backend.methods import auth
from calendar_backend.models.db import ApproveStatuses
from calendar_backend.models.db import Photo as DbPhoto
from calendar_backend.routes.models import (
    Photo,
)

lecturer_photo_review_router = APIRouter(prefix="/timetable/lecturer/{lecturer_id}/photo", tags=["Lecturer: Photo Review"])


@lecturer_photo_review_router.get("/review/", response_model=list[Photo])
async def get_unreviewed_photos(lecturer_id: int, _: auth.User = Depends(auth.get_current_user)) -> list[Photo]:
    photos = (
        DbPhoto.get_all(session=db.session, only_approved=False)
        .filter(DbPhoto.lecturer_id == lecturer_id, DbPhoto.approve_status == ApproveStatuses.PENDING)
        .all()
    )
    return parse_obj_as(list[Photo], photos)


@lecturer_photo_review_router.post("/{id}/review/", response_model=Photo)
async def review_photo(
    id: int,
    lecturer_id: int,
    action: Literal[ApproveStatuses.APPROVED, ApproveStatuses.DECLINED] = ApproveStatuses.DECLINED,
    _: auth.User = Depends(auth.get_current_user),
) -> Photo:
    photo = DbPhoto.get(id, only_approved=False, session=db.session)
    if photo.lecturer_id != lecturer_id or photo.approve_status is not ApproveStatuses.PENDING:
        raise ObjectNotFound(DbPhoto, id)
    DbPhoto.update(photo.id, approve_status=action, session=db.session)
    if action == ApproveStatuses.DECLINED:
        DbPhoto.delete(photo.id, session=db.session)
    db.session.flush()
    return Photo.from_orm(photo)