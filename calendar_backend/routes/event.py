import logging
from typing import Any

from fastapi import APIRouter
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import utils
from calendar_backend.routes.models import Event, EventPatch, EventPost, GetListEvent

event_router = APIRouter(prefix="/timetable/event", tags=["Event"])
settings = get_settings()
logger = logging.getLogger(__name__)


@event_router.get("/{id}", response_model=Event)
async def http_get_event_by_id(id: int) -> Event:
    logger.debug(f"Getting event id:{id}")
    return Event.from_orm(await utils.get_lesson_by_id(id, db.session))


@event_router.get("/", response_model=GetListEvent)
async def http_get_events(filter_name: str | None = None) -> dict[str, Any]:
    logger.debug(f"Getting events, filter:{filter_name}")
    result = await utils.get_list_lessons(db.session, filter_name)
    if isinstance(result, list):
        return {"items": [Event.from_orm(row) for row in result]}
    return {"items": [Event.from_orm(result)]}


@event_router.post("/", response_model=Event)
async def http_create_event(lesson: EventPost) -> Event:
    logger.debug(f"Creating lesson name:{lesson}")
    return Event.from_orm(
        await utils.create_lesson(
            lesson.room_id, lesson.lecturer_id, lesson.group_id, lesson.name, lesson.start_ts, lesson.end_ts, db.session
        )
    )


@event_router.patch("/{id}", response_model=Event)
async def http_patch_event(id: int, lesson_pydantic: EventPatch) -> Event:
    logger.debug(f"Patcing event id:{id}")
    lesson = await utils.get_lesson_by_id(id, db.session)
    return Event.from_orm(
        await utils.update_lesson(
            lesson,
            db.session,
            lesson_pydantic.name,
            lesson_pydantic.room_id,
            lesson.group_id,
            [row.id for row in lesson.lecturer],
            lesson.start_ts,
            lesson_pydantic.end_ts,
        )
    )


@event_router.delete("/{id}", response_model=None)
async def http_delete_event(id: int) -> None:
    logger.debug(f"Deleting event id:{id}")
    lesson = await utils.get_lesson_by_id(id, db.session)
    return await utils.delete_lesson(lesson, db.session)
