import datetime
import logging
from typing import Any

from fastapi import APIRouter
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import utils
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
    if start and end:
        return LecturerEvents(
            **lecturer.dict(), events=await utils.get_lecturer_lessons_in_daterange(lecturer, start, end)
        )
    return LecturerEvents(**lecturer.dict())


@lecturer_router.get("/", response_model=GetListLecturer)
async def http_get_lecturers(
    filter_name: str = ""
) -> dict[str, Any]:
    logger.debug(f"Getting rooms list, filter: {filter_name}")
    result = await utils.get_list_lecturers(db.session, filter_name)
    if not result:
        return {"items": []}
    if isinstance(result, list):
        return {"items": [Lecturer.from_orm(row) for row in result]}
    return {"items": [Lecturer.from_orm(result)]}


@lecturer_router.post("/", response_model=Lecturer)
async def http_create_lecturer(lecturer: LecturerPost) -> Lecturer:
    logger.debug(f"Creating lecturer:{lecturer}")
    return Lecturer.from_orm(
        await utils.create_lecturer(lecturer.first_name, lecturer.middle_name, lecturer.last_name, db.session)
    )


@lecturer_router.patch("/{id}", response_model=Lecturer)
async def http_patch_lecturer(id: int, lecturer_pydantic: LecturerPatch) -> Lecturer:
    logger.debug(f"Patching lecturer id:{id}")
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    return Lecturer.from_orm(
        await utils.update_lecturer(
            lecturer,
            db.session,
            lecturer_pydantic.first_name,
            lecturer_pydantic.middle_name,
            lecturer_pydantic.last_name,
        )
    )


@lecturer_router.delete("/{id}", response_model=None)
async def http_delete_lecturer(id: int) -> None:
    logger.debug(f"Deleting lectuer id:{id}")
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    return await utils.delete_lecturer(lecturer, db.session)
