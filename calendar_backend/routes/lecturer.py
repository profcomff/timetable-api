import datetime
import logging
from tempfile import NamedTemporaryFile
from typing import Any, Literal, IO

from fastapi import APIRouter, Depends, UploadFile, File, Query, Header, HTTPException
from fastapi_sqlalchemy import db
from starlette import status

from calendar_backend import get_settings
from calendar_backend.methods import utils, auth
from calendar_backend.routes.models import Lecturer, LecturerPatch, LecturerPost, GetListLecturer, LecturerEvents, \
    CommentLecturer, LecturerPhotos, Photo

lecturer_router = APIRouter(prefix="/timetable/lecturer", tags=["Lecturer"])
settings = get_settings()
logger = logging.getLogger(__name__)


async def valid_content_length(content_length: int = Header(..., lt=80_000)):
    return content_length


@lecturer_router.get("/{id}", response_model=LecturerEvents)
async def http_get_lecturer_by_id(
    id: int, start: datetime.date | None = None, end: datetime.date | None = None
) -> LecturerEvents:
    logger.debug(f"Getting lecturer id:{id}")
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    lecturer.photo_link = lecturer.avatar.link if lecturer.avatar else None
    result = LecturerEvents.from_orm(lecturer)
    if start and end:
        result.events = await utils.get_lecturer_lessons_in_daterange(lecturer, start, end)
    return result


@lecturer_router.get("/", response_model=GetListLecturer)
async def http_get_lecturers(
    query: str = "", limit: int = 10, offset: int = 0, details: list[Literal["photo", "description", "comments", ""]] = Query(...)
) -> dict[str, Any]:
    logger.debug(f"Getting rooms list, filter: {query}")
    list_lecturer, total = await utils.get_list_lecturers(db.session, query, limit, offset)
    result = [Lecturer.from_orm(row) for row in list_lecturer]
    if "photo" not in details:
        for row in result:
            row.avatar_id = None
    if "description" not in details:
        for row in result:
            row.description = None
    if "comments" not in details:
        for row in result:
            row.comments = None
    return {"items": result, "limit": limit, "offset": offset, "total": total}


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
    id: int, lecturer_pydantic: LecturerPatch, current_user: auth.User = Depends(auth.get_current_user)
) -> Lecturer:
    logger.debug(f"Patching lecturer id:{id}", extra={"user": current_user})
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    return Lecturer.from_orm(
        await utils.update_lecturer(
            lecturer,
            db.session,
            lecturer_pydantic.first_name,
            lecturer_pydantic.middle_name,
            lecturer_pydantic.last_name,
            lecturer_pydantic.description,
        )
    )


@lecturer_router.delete("/{id}", response_model=None)
async def http_delete_lecturer(id: int, current_user: auth.User = Depends(auth.get_current_user)) -> None:
    logger.debug(f"Deleting lectuer id:{id}", extra={"user": current_user})
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    return await utils.delete_lecturer(lecturer, db.session)


@lecturer_router.post("/{id}/photo", response_model=Photo)
async def http_upload_photo(id: int, photo: UploadFile = File(...), file_size: int = Depends(valid_content_length)) -> Photo:
    real_file_size = 0
    temp: IO = NamedTemporaryFile(delete=False)
    for chunk in photo.file:
        real_file_size += len(chunk)
        if real_file_size > file_size:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Too large")
        temp.write(chunk)
    return Photo.from_orm(await utils.upload_lecturer_photo(id, db.session, file=photo))


@lecturer_router.get("/{id}/photo", response_model=LecturerPhotos)
async def http_get_lecturer_photos(id: int) -> LecturerPhotos:
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    lecturer.links = [row.link for row in lecturer.photos]
    return LecturerPhotos.from_orm(lecturer)


@lecturer_router.post("/{id}/comment", response_model=CommentLecturer)
async def http_comment_lecturer(id: int, comment_text: str, author_name: str) -> CommentLecturer:
    return CommentLecturer.from_orm(await utils.create_comment_lecturer(id, db.session, comment_text, author_name))


@lecturer_router.patch("/{id}/comment", response_model=CommentLecturer)
async def http_update_comment_lecturer(comment_id: int, new_text: str) -> CommentLecturer:
    return CommentLecturer.from_orm(await utils.update_comment_lecturer(comment_id, db.session, new_text))


@lecturer_router.post("/{id}/avatar", response_model=Lecturer)
async def http_set_lecturer_avatar(id: int, photo_id: int) -> Lecturer:
    return Lecturer.from_orm(await utils.set_lecturer_avatar(id, photo_id, db.session))