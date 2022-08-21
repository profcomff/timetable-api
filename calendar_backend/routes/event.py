import datetime
import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db
from pydantic import Field

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
async def http_get_events(
    start: datetime.date = Field(default_factory=datetime.datetime.today()),
    end: datetime.date = Field(default_factory=datetime.datetime.today() + datetime.timedelta(days=1)),
    group_id: int | None = None,
    lecturer_id: int | None = None,
    room_id: int | None = None,
) -> GetListEvent:
    if not group_id and not lecturer_id and not room_id:
        raise HTTPException(status_code=400, detail=f"One argument reqiured, but no one received")
    if group_id:
        logger.debug(f"Getting events for group_id:{group_id}")
        if lecturer_id or room_id:
            raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
        return GetListEvent(
            **{
                "items": await utils.get_group_lessons_in_daterange(
                    await utils.get_group_by_id(group_id, db.session), start, end
                )
            }
        )
    if lecturer_id:
        logger.debug(f"Getting events for lecturer_id:{lecturer_id}")
        if group_id or room_id:
            raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
        return GetListEvent(
            **{
                "items": await utils.get_lecturer_lessons_in_daterange(
                    await utils.get_lecturer_by_id(lecturer_id, db.session), start, end
                )
            }
        )
    if room_id:
        logger.debug(f"Getting events for room_id:{room_id}")
        if lecturer_id or group_id:
            raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
        return GetListEvent(
            **{
                "items": await utils.get_room_lessons_in_daterange(
                    await utils.get_room_by_id(room_id, db.session), start, end
                )
            }
        )


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
