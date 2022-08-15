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
    try:
        return Lecturer.from_orm(await utils.get_lecturer_by_id(id, db.session))
    except exceptions.NoTeacherFoundError as e:
        logger.info(f"Lecturer id:{id} not found, error {e} occurred")
        raise HTTPException(status_code=404, detail="Not found")
    except ValueError as e:
        logger.info(f"Failed to parse lecturer id:{id}, error {e} occurred")
        raise HTTPException(status_code=500, detail="Error")


@lecturer_router.get("/", response_model=list[Lecturer])
async def http_get_lecturers(
    filter_first_name: str | None, filter_middle_name: str | None, filter_last_name: str
) -> list[Lecturer]:
    logger.debug(f"Getting rooms list, filter: {filter_last_name}, {filter_middle_name}, {filter_last_name}")
    try:
        return [
            Lecturer.from_orm(row)
            for row in await utils.get_list_lecturers(
                db.session, filter_first_name, filter_middle_name, filter_last_name
            )
        ]
    except ValueError as e:
        logger.info(
            f"Failed to parse lecturer list, filter: {filter_last_name} {filter_middle_name} {filter_last_name}, error {e} occurred"
        )
        raise HTTPException(status_code=500, detail="Error")


@lecturer_router.post("/", response_model=Lecturer)
async def http_create_lecturer(lecturer: Lecturer) -> Lecturer:
    logger.debug(f"Creating lecturer:{lecturer}")
    try:
        return Lecturer.from_orm(
            await utils.create_lecturer(lecturer.first_name, lecturer.middle_name, lecturer.last_name, db.session)
        )
    except ValueError as e:
        logger.info(f"Failed too create lecturer:{lecturer}, error {e} occurred")
        raise HTTPException(status_code=500, detail="Error")


@lecturer_router.post("/{id}", response_model=Lecturer)
async def http_patch_lecturer(
    id: int, new_first_name: str | None = None, new_middle_name: str | None = None, new_last_name: str | None = None
) -> Lecturer:
    logger.debug(f"Patching lecturer id:{id}")
    try:
        lecturer = await utils.get_lecturer_by_id(id, db.session)
        return Lecturer.from_orm(
            await utils.update_lecturer(lecturer, db.session, new_first_name, new_middle_name, new_last_name)
        )
    except exceptions.NoTeacherFoundError as e:
        logger.info(f"Lecturer id:{id} not found, error {e} occurred")
        raise HTTPException(status_code=404, detail="Not found")
    except ValueError as e:
        logger.info(f"Failed to parse lecturer id:{id}, errro {e} occurred")
        raise HTTPException(status_code=500, detail="Error")


@lecturer_router.delete("/{id}", response_model=None)
async def http_delete_lecturer(id: int) -> None:
    logger.debug(f"Deleting lectuer id:{id}")
    try:
        lecturer = await utils.get_lecturer_by_id(id, db.session)
        return await utils.delete_lecturer(lecturer, db.session)
    except exceptions.NoTeacherFoundError as e:
        logger.info(f"Lecturer id:{id} not found, error {e} occurred")
        raise HTTPException(status_code=404, detail="Not found")
