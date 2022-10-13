import logging
from typing import Any

from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from calendar_backend.exceptions import ObjectNotFound
from calendar_backend.methods import auth
from calendar_backend.models.db import Lecturer, ApproveStatuses
from calendar_backend.models.db import Photo as DbPhoto
from calendar_backend.routes.models import (
    GetListLecturer,
    LecturerGet,
    LecturerPost,
    LecturerPatch,
)
from calendar_backend.settings import get_settings

lecturer_router = APIRouter(prefix="/timetable/lecturer", tags=["Lecturer"])
review_lecturer_router = APIRouter(prefix="/timetable/lecturer/{lecturer_id}", tags=["Review"])
settings = get_settings()
logger = logging.getLogger(__name__)


@lecturer_router.get("/{id}", response_model=LecturerGet)
async def get_lecturer_by_id(id: int) -> LecturerGet:
    lecturer = Lecturer.get(id, session=db.session)
    if lecturer.avatar_id:
        lecturer.avatar_link = lecturer.avatar.link
    return LecturerGet.from_orm(Lecturer.get(id, session=db.session))


@lecturer_router.get("/", response_model=GetListLecturer)
async def get_lecturers(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
) -> dict[str, Any]:
    res = Lecturer.get_all(session=db.session).filter(Lecturer.search(query))
    if limit:
        cnt, res = res.count(), res.offset(offset).limit(limit).all()
    else:
        cnt, res = res.count(), res.offset(offset).all()
    for row in res:
        row.avatar_link = row.avatar.link if row.avatar else None
    result = [LecturerGet.from_orm(row) for row in res]
    return {
        "items": result,
        "limit": limit,
        "offset": offset,
        "total": cnt,
    }


@lecturer_router.post("/", response_model=LecturerGet)
async def create_lecturer(lecturer: LecturerPost, _: auth.User = Depends(auth.get_current_user)) -> LecturerGet:
    return LecturerGet.from_orm(Lecturer.create(session=db.session, **lecturer.dict()))


@lecturer_router.patch("/{id}", response_model=LecturerGet)
async def patch_lecturer(
    id: int, lecturer_inp: LecturerPatch, _: auth.User = Depends(auth.get_current_user)
) -> LecturerGet:
    if lecturer_inp.avatar_id:
        photo = DbPhoto.get(lecturer_inp.avatar_id, session=db.session)
        if photo.lecturer_id != id or photo.approve_status != ApproveStatuses.APPROVED:
            raise ObjectNotFound(DbPhoto, lecturer_inp.avatar_id)
        lecturer_upd = Lecturer.update(
            id, session=db.session, **lecturer_inp.dict(exclude_unset=True), avatar_link=photo.link
        )
    else:
        lecturer_upd = Lecturer.update(id, session=db.session, **lecturer_inp.dict(exclude_unset=True))
    return LecturerGet.from_orm(lecturer_upd)


@lecturer_router.delete("/{id}", response_model=None)
async def delete_lecturer(id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    Lecturer.delete(id, session=db.session)
