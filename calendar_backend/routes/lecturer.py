import logging

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import utils
from calendar_backend.routes.models import Lecturer, LecturerPostPatch

lecturer_router = APIRouter(prefix="/timetable/lecturer", tags=["Lecturer"])
settings = get_settings()
logger = logging.getLogger(__name__)


@lecturer_router.get("/{id}", response_model=Lecturer)
async def http_get_lecturer_by_id(id: int) -> Lecturer:
    logger.debug(f"Getting lecturer id:{id}")
    return Lecturer.from_orm(await utils.get_lecturer_by_id(id, db.session))


@lecturer_router.get("/", response_model=list[Lecturer])
async def http_get_lecturers(
    filter_first_name: str | None = None, filter_middle_name: str | None = None, filter_last_name: str = None
) -> list[Lecturer]:
    logger.debug(f"Getting rooms list, filter: {filter_last_name}, {filter_middle_name}, {filter_last_name}")
    result = await utils.get_list_lecturers(db.session, filter_first_name, filter_middle_name, filter_last_name)
    if isinstance(result, list):
        return [Lecturer.from_orm(row) for row in result]
    return [Lecturer.from_orm(result)]


@lecturer_router.post("/", response_model=Lecturer)
async def http_create_lecturer(lecturer: LecturerPostPatch) -> Lecturer:
    logger.debug(f"Creating lecturer:{lecturer}")
    if not lecturer.first_name or not lecturer.middle_name or not lecturer.last_name:
        raise HTTPException(status_code=400, detail="All fields must be not None")
    return Lecturer.from_orm(await utils.create_lecturer(lecturer.first_name, lecturer.middle_name, lecturer.last_name, db.session))


@lecturer_router.patch("/{id}", response_model=Lecturer)
async def http_patch_lecturer(
    id: int, lecturer_pydantic: Lecturer
) -> Lecturer:
    logger.debug(f"Patching lecturer id:{id}")
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    return Lecturer.from_orm(
        await utils.update_lecturer(lecturer, db.session, lecturer_pydantic.first_name, lecturer_pydantic.middle_name, lecturer_pydantic.last_name)
    )


@lecturer_router.delete("/{id}", response_model=None)
async def http_delete_lecturer(id: int) -> None:
    logger.debug(f"Deleting lectuer id:{id}")
    lecturer = await utils.get_lecturer_by_id(id, db.session)
    return await utils.delete_lecturer(lecturer, db.session)
