import datetime
import logging
from typing import Any, Literal

from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from fastapi_sqlalchemy import db
from calendar_backend.models.db import Lecturer
from calendar_backend.models.db import CommentLecturer as DbCommentLecturer
from calendar_backend.models.db import Photo as DbPhoto

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
    CommentLecturer, LecturerCommentPost, LecturerCommentPatch, LecturerComments
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
async def http_create_lecturer(lecturer: LecturerPost, _: auth.User = Depends(auth.get_current_user)) -> LecturerGet:
    return LecturerGet.from_orm(Lecturer.create(session=db.session, **lecturer.dict()))


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
async def http_get_lecturer_photos(id: int, limit: int = 10,
    offset: int = 0) -> LecturerPhotos:
    lecturer = Lecturer.get(id, session=db.session)
    return LecturerPhotos(**{
        "items": [row.link for row in lecturer.photos],
        "limit": limit,
        "offset": offset,
        "total": len([row.link for row in lecturer.photos])
    })


@lecturer_router.post("/{lecturer_id}/comment/", response_model=CommentLecturer)
async def http_comment_lecturer(lecturer_id: int, comment: LecturerCommentPost) -> CommentLecturer:
    return CommentLecturer.from_orm(DbCommentLecturer.create(lecturer_id=lecturer_id, session=db.session, **comment.dict()))


@lecturer_router.patch("/{lecturer_id}/comment/{id}", response_model=CommentLecturer)
async def http_update_comment_lecturer(id: int, lecturer_id: int, comment_inp: LecturerCommentPatch) -> CommentLecturer:
    comment = DbCommentLecturer.update(id, session=db.session, **comment_inp.dict(exclude_unset=True))
    if comment.lecturer_id != lecturer_id:
        raise HTTPException(status_code=404, detail=f"Comment id:{id} not found in lecturer:{lecturer_id} comments list")
    return CommentLecturer.from_orm(comment)


@lecturer_router.post("/{id}/avatar", response_model=LecturerGet)
async def http_set_lecturer_avatar(id: int, photo_id: int) -> LecturerGet:
    return LecturerGet.from_orm(await utils.set_lecturer_avatar(id, photo_id, db.session))


@lecturer_router.delete("/{lecturer_id}/comment/{id}", response_model=None)
async def http_delete_comment(id: int, lecturer_id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    comment = DbCommentLecturer.get(id, session=db.session)
    if comment.lecturer_id != lecturer_id:
        raise HTTPException(status_code=404, detail=f"Comment id:{id} not found in lecturer:{lecturer_id} comments list")
    return DbCommentLecturer.delete(id=id, session=db.session)


@lecturer_router.get("/{lecturer_id}/comment/{id}", response_model=CommentLecturer)
async def http_get_comment(id: int, lecturer_id: int) -> CommentLecturer:
    comment = DbCommentLecturer.get(id, session=db.session)
    if not comment.lecturer_id == lecturer_id:
        raise HTTPException(status_code=404, detail=f"Comment id:{id} not found in lecturer:{lecturer_id} comments list")
    return CommentLecturer.from_orm(comment)


@lecturer_router.delete("/{id}/photo", response_model=None)
async def http_delete_photo(id: int) -> None:
    return DbPhoto.delete(id=id, session=db.session)


@lecturer_router.get("/{lecturer_id}/comment/", response_model=LecturerComments)
async def http_get_all_lecturer_comments(lecturer_id: int, limit: int = 10, offset: int = 0) -> LecturerComments:
    lecturer = Lecturer.get(lecturer_id, session=db.session)
    return LecturerComments(**{
        "items": lecturer.comments,
        "limit": limit,
        "offset": offset,
        "total": len(lecturer.comments)
    })

