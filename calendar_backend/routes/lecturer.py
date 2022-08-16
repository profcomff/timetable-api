import logging

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db

from calendar_backend import exceptions
from calendar_backend import get_settings
from calendar_backend.methods import utils
from calendar_backend.routes.models import Lecturer

lecturer_router = APIRouter(prefix="/timetable/lecturer", tags=["Lecturer"])
settings = get_settings()
logger = logging.getLogger(__name__)


@lecturer_router.get("/{id}", response_model=Lecturer)
async def http_get_lecturer_by_id(id: int) -> Lecturer:
    logger.debug(f"Getting lecturer id:{id}")
    return Lecturer.from_orm(await utils.get_lecturer_by_id(id, db.session))


@lecturer_router.get("/", response_model=list[Lecturer])
async def http_get_lecturers(
    filter_first_name: str | None, filter_middle_name: str | None, filter_last_name: str
) -> list[Lecturer]:
    logger.debug(f"Getting rooms list, filter: {filter_last_name}, {filter_middle_name}, {filter_last_name}")
    result = await utils.get_list_lecturers(
            db.session, filter_first_name, filter_middle_name, filter_last_name
        )
    if isinstance(result, list):
        return [
            Lecturer.from_orm(row)
            for row in result
        ]
    return [Lecturer.from_orm(result)]


@lecturer_router.post("/", response_model=Lecturer)
async def http_create_lecturer(first_name: str, middle_name: str, last_name: str) -> Lecturer:
    logger.debug(f"Creating lecturer:{first_name} {middle_name} {last_name}")
    return Lecturer.from_orm(
        await utils.create_lecturer(first_name, middle_name, last_name, db.session)
    )


@lecturer_router.post("/{id}", response_model=Lecturer)
async def http_patch_lecturer(
    id: int, new_first_name: str | None = None, new_middle_name: str | None = None, new_last_name: str | None = None
) -> Lecturer:
    logger.debug(f"Patching lecturer id:{id}")
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    return Lecturer.from_orm(
        await utils.update_lecturer(lecturer, db.session, new_first_name, new_middle_name, new_last_name)
    )


@lecturer_router.delete("/{id}", response_model=None)
async def http_delete_lecturer(id: int) -> None:
    logger.debug(f"Deleting lectuer id:{id}")
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    return await utils.delete_lecturer(lecturer, db.session)
