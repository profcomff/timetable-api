import datetime
import logging

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db

from calendar_backend import exceptions
from calendar_backend import get_settings
from calendar_backend.methods import utils
from calendar_backend.routes.models import Lesson

event_router = APIRouter(prefix="/timetable/event", tags=["Event"])
settings = get_settings()
logger = logging.getLogger(__name__)


@event_router.get("/{id}", response_model=Lesson)
async def http_get_event_by_id(id: int) -> Lesson:
    logger.debug(f"Getting event id:{id}")
    return Lesson.from_orm(await utils.get_lesson_by_id(id, db.session))


@event_router.get("/", response_model=list[Lesson])
async def http_get_events(filter_name: str | None = None) -> list[Lesson]:
    logger.debug(f"Getting events, filter:{filter_name}")
    result = await utils.get_list_lessons(db.session, filter_name)
    if isinstance(result, list):
        return [Lesson.from_orm(row) for row in result]
    return [Lesson.from_orm(result)]


@event_router.post("/", response_model=Lesson)
async def http_create_event(
    name: str, room_id: int, group_id: int, lecturer_id: int, start_ts: datetime.datetime, end_ts: datetime.datetime
) -> Lesson:
    logger.debug(
        f"Creating lesson name:{name}, room_id:{room_id}, lecturer_id:{lecturer_id}, group_id:{group_id}, start_ts:{start_ts}, end_ts: {end_ts}"
    )
    return Lesson.from_orm(
        await utils.create_lesson(room_id, lecturer_id, group_id, name, start_ts, end_ts, db.session)
    )


@event_router.post("/{id}", response_model=Lesson)
async def http_patch_event(
    id: int,
    new_name: str | None = None,
    new_room_id: int | None = None,
    new_group_id: int | None = None,
    new_lecturer_id: int | None = None,
    new_start_ts: datetime.datetime | None = None,
    new_end_ts: datetime.datetime | None = None,
) -> Lesson:
    logger.debug(f"Patcing event id:{id}")
    lesson = await utils.get_lesson_by_id(id, db.session)
    return Lesson.from_orm(
        await utils.update_lesson(
            lesson, db.session, new_name, new_room_id, new_group_id, new_lecturer_id, new_start_ts, new_end_ts
        )
    )


@event_router.delete("/{id}", response_model=None)
async def http_delete_event(id: int) -> None:
    logger.debug(f"Deleting event id:{id}")
    lesson = await utils.get_lesson_by_id(id, db.session)
    return await utils.delete_lesson(lesson, db.session)
