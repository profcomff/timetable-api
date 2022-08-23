import datetime
import logging
from typing import Any, Literal

from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import utils, auth
from calendar_backend.routes.models import Lecturer, LecturerPatch, LecturerPost, GetListLecturer, LecturerEvents

lecturer_router = APIRouter(prefix="/timetable/lecturer", tags=["Lecturer"])
settings = get_settings()
logger = logging.getLogger(__name__)


@lecturer_router.get("/{id}", response_model=LecturerEvents)
async def http_get_lecturer_by_id(
    id: int, start: datetime.date | None = None, end: datetime.date | None = None
) -> LecturerEvents:
    logger.debug(f"Getting lecturer id:{id}")
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    lecturer.photo_link = lecturer.avatar.link
    result = LecturerEvents.from_orm(lecturer)
    if start and end:
        result.events = await utils.get_lecturer_lessons_in_daterange(lecturer, start, end)
    return result


@lecturer_router.get("/", response_model=GetListLecturer)
async def http_get_lecturers(query: str = "", limit: int = 10, offset: int = 0, details: list[Literal["photo", "description", ""]] = Query(...)) -> dict[str, Any]:
    logger.debug(f"Getting rooms list, filter: {query}")
    result, total = await utils.get_list_lecturers(db.session, query, limit, offset)
    if "photo" in details:
        for row in result:
            row.photo_link = row.avatar.link
    if "description" not in details:
        for row in result:
            row.description = None
    return {"items": [Lecturer.from_orm(row) for row in result], "limit": limit, "offset": offset, "total": total}


@lecturer_router.post("/", response_model=Lecturer)
async def http_create_lecturer(
    lecturer: LecturerPost, current_user: auth.User = Depends(auth.get_current_user)
) -> Lecturer:
    logger.debug(f"Creating lecturer: {lecturer}", extra={"user": current_user})
    return Lecturer.from_orm(
        await utils.create_lecturer(lecturer.first_name, lecturer.middle_name, lecturer.last_name, lecturer.description, db.session)
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
            lecturer_pydantic.description
        )
    )


@lecturer_router.delete("/{id}", response_model=None)
async def http_delete_lecturer(id: int, current_user: auth.User = Depends(auth.get_current_user)) -> None:
    logger.debug(f"Deleting lectuer id:{id}", extra={"user": current_user})
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    return await utils.delete_lecturer(lecturer, db.session)


@lecturer_router.post("/{id}/photo")
async def http_upload_photo(id: int, photo: UploadFile = File(...), current_user: auth.User = Depends(auth.get_current_user)):
    return await utils.upload_lecturer_photo(id, db.session, file=photo)


@lecturer_router.get("/{id}/photo")
async def http_get_lecturer_photos(id: int):
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    return lecturer, [row.link for row in lecturer.photos]


@lecturer_router.post("/{id}/comment")
async def http_comment_lecturer(id: int, comment_text: str, author_name: str):
    return await utils.create_comment_lecturer(id, db.session, comment_text, author_name)


@lecturer_router.patch("/{id}/comment")
async def http_update_comment_lecturer(comment_id: int, new_text: str):
    return await utils.update_comment(comment_id, db.session, new_text)