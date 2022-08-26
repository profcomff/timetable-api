import datetime
import logging
from typing import Literal, Union

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi_sqlalchemy import db

from calendar_backend.settings import get_settings
from calendar_backend.methods import utils, auth, list_calendar
from calendar_backend.routes.models import (
    GetListEvent,
    GetListEventWithoutLecturerComments,
    GetListEventWithoutLecturerDescription,
    GetListEventWithoutLecturerDescriptionAndComments,
    EventWithoutLecturerDescriptionAndComments,
    EventPatch,
    CommentEvent,
    Event,
    EventPost,
)

event_router = APIRouter(prefix="/timetable/event", tags=["Event"])
settings = get_settings()
logger = logging.getLogger(__name__)


@event_router.get("/{id}", response_model=Event)
async def http_get_event_by_id(id: int) -> Event:
    return Event.from_orm(await utils.get_lesson_by_id(id, db.session, False))


@event_router.get(
    "/",
    response_model=Union[
        GetListEvent,
        GetListEventWithoutLecturerComments,
        GetListEventWithoutLecturerDescription,
        GetListEventWithoutLecturerDescriptionAndComments,
    ],
)
async def http_get_events(
    start: datetime.date | None = Query(default=None, description="Default: Today"),
    end: datetime.date | None = Query(default=None, description="Default: Tomorrow"),
    group_id: int | None = None,
    lecturer_id: int | None = None,
    room_id: int | None = None,
    detail: list[Literal["comment", "description", ""]] = Query(...),
    format: Literal["json", "ics"] = "json"
) -> Union[
    GetListEvent,
    GetListEventWithoutLecturerComments,
    GetListEventWithoutLecturerDescription,
    GetListEventWithoutLecturerDescriptionAndComments,
]:
    start = start or datetime.date.today()
    end = end or datetime.date.today() + datetime.timedelta(days=1)
    if not group_id and not lecturer_id and not room_id:
        raise HTTPException(status_code=400, detail=f"One argument reqiured, but no one received")
    match format:
        case "json":
            if group_id:
                logger.debug(f"Getting events for group_id:{group_id}")
                if lecturer_id or room_id:
                    raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
                list_events = await utils.get_group_lessons_in_daterange(
                    await utils.get_group_by_id(group_id, db.session, False), start, end
                )
            if lecturer_id:
                logger.debug(f"Getting events for lecturer_id:{lecturer_id}")
                if group_id or room_id:
                    raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
                list_events = await utils.get_lecturer_lessons_in_daterange(
                    await utils.get_lecturer_by_id(lecturer_id, db.session, False), start, end
                )
            if room_id:
                logger.debug(f"Getting events for room_id:{room_id}")
                if lecturer_id or group_id:
                    raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
                list_events = await utils.get_room_lessons_in_daterange(
                    await utils.get_room_by_id(room_id, db.session, False), start, end
                )
            if "" in detail:
                return GetListEventWithoutLecturerDescriptionAndComments(items=list_events)
            if "comment" not in detail and "description" in detail:
                return GetListEventWithoutLecturerComments(items=list_events)
            if "description" not in detail and "comment" in detail:
                return GetListEventWithoutLecturerDescription(items=list_events)
            return GetListEvent(items=list_events)
        case "ics":
            if not group_id:
                raise HTTPException(status_code=400, detail=f"'group_id' argument reqiured, but not received")
            return await list_calendar.create_ics(group_id, start, end, db.session)

@event_router.post("/", response_model=EventWithoutLecturerDescriptionAndComments)
async def http_create_event(
    lesson: EventPost, current_user: auth.User = Depends(auth.get_current_user)
) -> EventWithoutLecturerDescriptionAndComments:
    return EventWithoutLecturerDescriptionAndComments.from_orm(
        await utils.create_lesson(
            lesson.room_id, lesson.lecturer_id, lesson.group_id, lesson.name, lesson.start_ts, lesson.end_ts, db.session
        )
    )


@event_router.patch("/{id}", response_model=EventWithoutLecturerDescriptionAndComments)
async def http_patch_event(
    id: int, event_inp: EventPatch, current_user: auth.User = Depends(auth.get_current_user)
) -> EventWithoutLecturerDescriptionAndComments:
    lesson = await utils.get_lesson_by_id(id, db.session, True)
    return EventWithoutLecturerDescriptionAndComments.from_orm(
        await utils.update_lesson(
            lesson,
            db.session,
            event_inp.name,
            event_inp.room_id,
            lesson.group_id,
            [row.id for row in lesson.lecturer],
            lesson.start_ts,
            event_inp.end_ts,
            event_inp.is_deleted,
        )
    )


@event_router.delete("/{id}", response_model=None)
async def http_delete_event(id: int, current_user: auth.User = Depends(auth.get_current_user)) -> None:
    lesson = await utils.get_lesson_by_id(id, db.session, False)
    return await utils.delete_lesson(lesson, db.session)


@event_router.post("/{id}/comment", response_model=CommentEvent)
async def http_comment_event(id: int, author_name: str, text: str) -> CommentEvent:
    return CommentEvent.from_orm(await utils.create_comment_event(id, db.session, text, author_name))


@event_router.patch("/{id}/comment", response_model=CommentEvent)
async def http_udpate_comment(comment_id: int, new_text: str) -> CommentEvent:
    return CommentEvent.from_orm(await utils.update_comment_event(comment_id, db.session, new_text))
