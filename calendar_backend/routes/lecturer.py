import datetime
import logging
from typing import Any, Literal

from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi_sqlalchemy import db
from calendar_backend.models.db import Lecturer

from calendar_backend.settings import get_settings
from calendar_backend.methods import utils, auth
from calendar_backend.routes.models import (
    LecturerEvents,
    GetListLecturer,
    LecturerGet,
    LecturerPost,
    LecturerPatch,
    Photo,
    LecturerPhotos,
    CommentLecturer,
)

lecturer_router = APIRouter(prefix="/timetable/lecturer", tags=["Lecturer"])
settings = get_settings()
logger = logging.getLogger(__name__)


@lecturer_router.get("/{id}", response_model=LecturerEvents)
async def http_get_lecturer_by_id(
    id: int, start: datetime.date | None = None, end: datetime.date | None = None
) -> LecturerEvents:
    lecturer = Lecturer.get(id, session=db.session)
    lecturer.avatar_link = lecturer.avatar.link if lecturer.avatar else None
    result = LecturerEvents.from_orm(lecturer)
    if start and end:
        result.events = await utils.get_lecturer_lessons_in_daterange(lecturer, start, end)
    return result


@lecturer_router.get("/", response_model=GetListLecturer)
async def http_get_lecturers(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    details: list[Literal["photo", "description", "comments", ""]] | None = Query([]),
) -> dict[str, Any]:
    res = Lecturer.get_all(session=db.session).filter(Lecturer.search(query))
    cnt, res = res.count(), res.offset(offset).limit(limit).all()
    for row in res:
        row.avatar_link = row.avatar.link if row.avatar else None
    result = [LecturerGet.from_orm(row) for row in res]
    exclude = []
    details = details or [""]
    if "" in details:
        exclude.append(["photo", "description", "comments"])
    if "photo" not in details:
        exclude.append("photo")
    if "description" not in details:
        exclude.append("description")
    if "comments" not in details:
        exclude.append("comments")
    return {
        "items": [row.dict(exclude={*exclude}) for row in result],
        "limit": limit,
        "offset": offset,
        "total": cnt,
    }


@lecturer_router.post("/", response_model=LecturerGet)
async def http_create_lecturer(lecturer: LecturerPost, _: auth.User = Depends(auth.get_current_user)) -> LecturerGet:
    return Lecturer.create(session=db.session, **lecturer.dict())


@lecturer_router.patch("/{id}", response_model=LecturerGet)
async def http_patch_lecturer(
    id: int, lecturer_inp: LecturerPatch, _: auth.User = Depends(auth.get_current_user)
) -> LecturerGet:
    lecturer = Lecturer.update(id, session=db.session, **lecturer_inp.dict(exclude_unset=True))
    return LecturerGet.from_orm(lecturer)


@lecturer_router.delete("/{id}", response_model=None)
async def http_delete_lecturer(id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    Lecturer.delete(id, session=db.session)


@lecturer_router.post("/{id}/photo", response_model=Photo)
async def http_upload_photo(id: int, photo: UploadFile = File(...)) -> Photo:
    return Photo.from_orm(await utils.upload_lecturer_photo(id, db.session, file=photo))


@lecturer_router.get("/{id}/photo", response_model=LecturerPhotos)
async def http_get_lecturer_photos(id: int) -> LecturerPhotos:
    lecturer = Lecturer.get(id, session=db.session)
    lecturer.links = [row.link for row in lecturer.photos]
    return LecturerPhotos.from_orm(lecturer)


@lecturer_router.post("/{id}/comment", response_model=CommentLecturer)
async def http_comment_lecturer(id: int, comment_text: str, author_name: str) -> CommentLecturer:
    return CommentLecturer.from_orm(await utils.create_comment_lecturer(id, db.session, comment_text, author_name))


@lecturer_router.patch("/{id}/comment", response_model=CommentLecturer)
async def http_update_comment_lecturer(comment_id: int, new_text: str) -> CommentLecturer:
    return CommentLecturer.from_orm(await utils.update_comment_lecturer(comment_id, db.session, new_text))


@lecturer_router.post("/{id}/avatar", response_model=LecturerGet)
async def http_set_lecturer_avatar(id: int, photo_id: int) -> LecturerGet:
    return LecturerGet.from_orm(await utils.set_lecturer_avatar(id, photo_id, db.session))
