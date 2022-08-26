import datetime
import logging
from typing import Any, Literal

from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi_sqlalchemy import db

from calendar_backend.settings import get_settings
from calendar_backend.methods import utils, auth
from calendar_backend.routes.models import (
    LecturerEvents,
    GetListLecturer,
    Lecturer,
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
    logger.debug(f"Getting lecturer id:{id}")
    lecturer = await utils.get_lecturer_by_id(id, db.session, False)
    lecturer.photo_link = lecturer.avatar.link if lecturer.avatar else None
    result = LecturerEvents.from_orm(lecturer)
    if start and end:
        result.events = await utils.get_lecturer_lessons_in_daterange(lecturer, start, end)
    return result


@lecturer_router.get("/", response_model=GetListLecturer)
async def http_get_lecturers(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    details: list[Literal["photo", "description", "comments", ""]] = Query(...),
) -> dict[str, Any]:
    logger.debug(f"Getting rooms list, filter: {query}")
    list_lecturer, total = await utils.get_list_lecturers(db.session, query, limit, offset)
    result = [Lecturer.from_orm(row) for row in list_lecturer]
    exclude = []
    if "" in details:
        exclude.append(["photo", "description", "comments"])
    if "photo" not in details:
        exclude.append("photo")
    if "description" not in details:
        exclude.append("description")
    if "comments" not in details:
        exclude.append("comments")
    return {"items": [row.dict(exclude={*exclude}) for row in result], "limit": limit, "offset": offset, "total": total}


@lecturer_router.post("/", response_model=Lecturer)
async def http_create_lecturer(
    lecturer: LecturerPost, current_user: auth.User = Depends(auth.get_current_user)
) -> Lecturer:
    logger.debug(f"Creating lecturer: {lecturer}", extra={"user": current_user})
    return Lecturer.from_orm(
        await utils.create_lecturer(
            lecturer.first_name, lecturer.middle_name, lecturer.last_name, lecturer.description, db.session
        )
    )


@lecturer_router.patch("/{id}", response_model=Lecturer)
async def http_patch_lecturer(
    id: int, lecturer_inp: LecturerPatch, current_user: auth.User = Depends(auth.get_current_user)
) -> Lecturer:
    logger.debug(f"Patching lecturer id:{id}", extra={"user": current_user})
    lecturer = await utils.get_lecturer_by_id(id, db.session, True)
    return Lecturer.from_orm(
        await utils.update_lecturer(
            lecturer,
            db.session,
            lecturer_inp.first_name,
            lecturer_inp.middle_name,
            lecturer_inp.last_name,
            lecturer_inp.description,
            lecturer_inp.is_deleted,
        )
    )


@lecturer_router.delete("/{id}", response_model=None)
async def http_delete_lecturer(id: int, current_user: auth.User = Depends(auth.get_current_user)) -> None:
    logger.debug(f"Deleting lectuer id:{id}", extra={"user": current_user})
    lecturer = await utils.get_lecturer_by_id(id, db.session, False)
    return await utils.delete_lecturer(lecturer, db.session)


@lecturer_router.post("/{id}/photo", response_model=Photo)
async def http_upload_photo(id: int, photo: UploadFile = File(...)) -> Photo:
    logger.debug(f"Uploading photo for lecturer: {id}")
    return Photo.from_orm(await utils.upload_lecturer_photo(id, db.session, file=photo))


@lecturer_router.get("/{id}/photo", response_model=LecturerPhotos)
async def http_get_lecturer_photos(id: int) -> LecturerPhotos:
    logger.debug(f"Getting lecturer: {id} photos")
    lecturer = await utils.get_lecturer_by_id(id, db.session, False)
    lecturer.links = [row.link for row in lecturer.photos]
    return LecturerPhotos.from_orm(lecturer)


@lecturer_router.post("/{id}/comment", response_model=CommentLecturer)
async def http_comment_lecturer(id: int, comment_text: str, author_name: str) -> CommentLecturer:
    logger.debug(f"Creating comment to lecturer: {id}")
    return CommentLecturer.from_orm(await utils.create_comment_lecturer(id, db.session, comment_text, author_name))


@lecturer_router.patch("/{id}/comment", response_model=CommentLecturer)
async def http_update_comment_lecturer(comment_id: int, new_text: str) -> CommentLecturer:
    logger.debug(f"Updating comment id:{id}")
    return CommentLecturer.from_orm(await utils.update_comment_lecturer(comment_id, db.session, new_text))


@lecturer_router.post("/{id}/avatar", response_model=Lecturer)
async def http_set_lecturer_avatar(id: int, photo_id: int) -> Lecturer:
    logger.debug(f"Setting lecturer: {id} avatar(photo: {photo_id}")
    return Lecturer.from_orm(await utils.set_lecturer_avatar(id, photo_id, db.session))
