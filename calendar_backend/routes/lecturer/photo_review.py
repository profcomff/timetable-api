from typing import Literal

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from sqlalchemy.orm import Query

from calendar_backend.methods.image import get_photo_webpath
from calendar_backend.models.db import ApproveStatuses
from calendar_backend.models.db import Photo as DbPhoto
from calendar_backend.routes.models import Action, Photo
from calendar_backend.routes.models.base import Base as BaseSchema


router = APIRouter(prefix="/lecturer/photo", tags=["Lecturer: Photo Review"])


class Photo(BaseSchema):
    id: int
    lecturer_id: int
    link: str


class PhotoListResponse(BaseSchema):
    items: list[Photo]
    limit: int
    offset: int
    total: int


@router.get("/review", response_model=PhotoListResponse)
async def get_unreviewed_photos(
    limit: int = 10,
    offset: int = 0,
    order_by: Literal['lecturer_id'] | None = None,
    lecturer_id: int = None,
    _=Depends(UnionAuth(scopes=["timetable.lecturer.photo.review"])),
):
    query: Query = DbPhoto.get_all(session=db.session, only_approved=False)
    query = query.filter(DbPhoto.approve_status == ApproveStatuses.PENDING)
    if lecturer_id:
        query = query.filter(DbPhoto.lecturer_id == lecturer_id)
    if order_by:
        query = query.order_by(order_by)
    query = query.order_by('id')
    if limit:
        cnt, query = query.count(), query.offset(offset).limit(limit)
    else:
        cnt, query = query.count(), query.offset(offset)
    query = query.all()

    result = []
    for row in query:
        get_row = Photo.from_orm(row)
        get_row.link = get_photo_webpath(row.link)
        result.append(get_row)

    return PhotoListResponse(
        items=result,
        limit=limit,
        offset=offset,
        total=cnt,
    )


@router.post("/{id}/review", response_model=Photo | None)
async def review_photo(
    id: int,
    action: Action,
    _=Depends(UnionAuth(scopes=["timetable.lecturer.photo.review"])),
) -> Photo:
    photo = DbPhoto.get(id, only_approved=False, session=db.session)
    DbPhoto.update(photo.id, approve_status=action.action, session=db.session)
    if action == ApproveStatuses.DECLINED:
        DbPhoto.delete(photo.id, session=db.session)
        db.session.flush()
        return None
    if not photo.lecturer.avatar:
        photo.lecturer.avatar_id = photo.id
    db.session.flush()
    return Photo.from_orm(photo)
