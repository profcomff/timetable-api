import logging
from typing import Any

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_sqlalchemy import db

from calendar_backend.exceptions import ObjectNotFound
from calendar_backend.methods import utils, auth
from calendar_backend.models.db import CommentLecturer as DbCommentLecturer
from calendar_backend.models.db import Lecturer
from calendar_backend.models.db import Photo as DbPhoto
from calendar_backend.routes.models import (
    GetListLecturer,
    LecturerGet,
    LecturerPost,
    LecturerPatch,
    Photo,
    LecturerPhotos,
    CommentLecturer,
    LecturerCommentPost,
    LecturerCommentPatch,
    LecturerComments,
)
from calendar_backend.settings import get_settings

lecturer_router = APIRouter(prefix="/timetable/lecturer", tags=["Lecturer"])
settings = get_settings()
logger = logging.getLogger(__name__)


@lecturer_router.get("/{id}", response_model=LecturerGet)
async def http_get_lecturer_by_id(
    id: int
) -> LecturerGet:
    return LecturerGet.from_orm(Lecturer.get(id, session=db.session))


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


@lecturer_router.post("/{lecturer_id}/photo", response_model=Photo)
async def http_upload_photo(lecturer_id: int, photo: UploadFile = File(...)) -> Photo:
    return Photo.from_orm(await utils.upload_lecturer_photo(lecturer_id, db.session, file=photo))


@lecturer_router.get("/{lecturer_id}/photo", response_model=LecturerPhotos)
async def http_get_lecturer_photos(lecturer_id: int, limit: int = 10, offset: int = 0) -> LecturerPhotos:
    res = DbPhoto.get_all(session=db.session).filter(DbPhoto.lecturer_id == lecturer_id)
    if limit:
        cnt, res = res.count(), res.offset(offset).limit(limit).all()
    else:
        cnt, res = res.count(), res.offset(offset).all()
    return LecturerPhotos(**{"items": [row.link for row in res], "limit": limit, "offset": offset, "total": cnt})


@lecturer_router.post("/{lecturer_id}/comment/", response_model=CommentLecturer)
async def http_comment_lecturer(lecturer_id: int, comment: LecturerCommentPost) -> CommentLecturer:
    return CommentLecturer.from_orm(
        DbCommentLecturer.create(lecturer_id=lecturer_id, session=db.session, **comment.dict())
    )


@lecturer_router.patch("/{lecturer_id}/comment/{id}", response_model=CommentLecturer)
async def http_update_comment_lecturer(id: int, lecturer_id: int, comment_inp: LecturerCommentPatch) -> CommentLecturer:
    comment = DbCommentLecturer.get(id=id, session=db.session)
    if comment.lecturer_id != lecturer_id:
        raise ObjectNotFound(DbCommentLecturer, id)
    return CommentLecturer.from_orm(
        DbCommentLecturer.update(id, session=db.session, **comment_inp.dict(exclude_unset=True))
    )


@lecturer_router.post("/{id}/avatar", response_model=LecturerGet)
async def http_set_lecturer_avatar(id: int, photo_id: int) -> LecturerGet:
    return LecturerGet.from_orm(await utils.set_lecturer_avatar(id, photo_id, db.session))


@lecturer_router.delete("/{lecturer_id}/comment/{id}", response_model=None)
async def http_delete_comment(id: int, lecturer_id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    comment = DbCommentLecturer.get(id, session=db.session)
    if comment.lecturer_id != lecturer_id:
        raise ObjectNotFound(DbCommentLecturer, id)
    return DbCommentLecturer.delete(id=id, session=db.session)


@lecturer_router.get("/{lecturer_id}/comment/{id}", response_model=CommentLecturer)
async def http_get_comment(id: int, lecturer_id: int) -> CommentLecturer:
    comment = DbCommentLecturer.get(id, session=db.session)
    if not comment.lecturer_id == lecturer_id:
        raise ObjectNotFound(DbCommentLecturer, id)
    return CommentLecturer.from_orm(comment)


@lecturer_router.delete("/{lecturer_id}/photo/{id}", response_model=None)
async def http_delete_photo(id: int, lecturer_id: int) -> None:
    photo = DbPhoto.get(id, session=db.session)
    if photo.lecturer_id != lecturer_id:
        raise ObjectNotFound(DbPhoto, id)
    return DbPhoto.delete(id=id, session=db.session)


@lecturer_router.get("/{lecturer_id}/comment/", response_model=LecturerComments)
async def http_get_all_lecturer_comments(lecturer_id: int, limit: int = 10, offset: int = 0) -> LecturerComments:
    res = DbCommentLecturer.get_all(session=db.session).filter(DbCommentLecturer.lecturer_id == lecturer_id)
    if limit:
        cnt, res = res.count(), res.offset(offset).limit(limit).all()
    else:
        cnt, res = res.count(), res.offset(offset).all()
    return LecturerComments(**{"items": res, "limit": limit, "offset": offset, "total": cnt})


@lecturer_router.get("/{lecturer_id}/photo/{id}", response_model=Photo)
async def get_photo(id: int, lecturer_id: int) -> Photo:
    photo = DbPhoto.get(id, session=db.session)
    if photo.lecturer_id != lecturer_id:
        raise ObjectNotFound(DbPhoto, id)
    return Photo.from_orm(photo)
