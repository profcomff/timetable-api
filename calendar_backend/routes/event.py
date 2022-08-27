import datetime
import logging
from typing import Literal, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_sqlalchemy import db

from calendar_backend.methods import auth, list_calendar, utils
from calendar_backend.models import Group, Room, Lecturer, Event, CommentEvent
from calendar_backend.routes.models import (
    CommentEventGet,
    EventGet,
    EventPatch,
    EventPost,
    EventWithoutLecturerDescriptionAndComments,
    GetListEvent,
    GetListEventWithoutLecturerComments,
    GetListEventWithoutLecturerDescription,
    GetListEventWithoutLecturerDescriptionAndComments,
)
from calendar_backend.settings import get_settings


event_router = APIRouter(prefix="/timetable/event", tags=["Event"])
settings = get_settings()
logger = logging.getLogger(__name__)


@event_router.get("/{id}", response_model=EventGet)
async def http_get_event_by_id(id: int) -> EventGet:
    return EventGet.from_orm(Event.get(id, session=db.session))


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
    format: Literal["json", "ics"] = "json",
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
                    Group.get(group_id, session=db.session), start, end
                )
            if lecturer_id:
                logger.debug(f"Getting events for lecturer_id:{lecturer_id}")
                if group_id or room_id:
                    raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
                list_events = await utils.get_lecturer_lessons_in_daterange(
                    Lecturer.get(lecturer_id, session=db.session), start, end
                )
            if room_id:
                logger.debug(f"Getting events for room_id:{room_id}")
                if lecturer_id or group_id:
                    raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
                list_events = await utils.get_room_lessons_in_daterange(
                    Room.get(room_id, session=db.session), start, end
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
    event: EventPost, _: auth.User = Depends(auth.get_current_user)
) -> EventWithoutLecturerDescriptionAndComments:
    event_dict = event.dict()
    rooms = [Room.get(room_id, session=db.session) for room_id in event_dict.pop("room_id", [])]
    lecturers = [Lecturer.get(lecturer_id, session=db.session) for lecturer_id in event_dict.pop("lecturer_id", [])]
    return EventWithoutLecturerDescriptionAndComments.from_orm(
        Event.create(
            **event_dict,
            room=rooms,
            lecturer=lecturers,
            session=db.session,
        )
    )


@event_router.patch("/{id}", response_model=EventWithoutLecturerDescriptionAndComments)
async def http_patch_event(
    id: int, event_inp: EventPatch, _: auth.User = Depends(auth.get_current_user)
) -> EventWithoutLecturerDescriptionAndComments:
    return Event.update(id, session=db.session, **event_inp.dict(exclude_unset=True))


@event_router.delete("/{id}", response_model=None)
async def http_delete_event(id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    Event.delete(id, session=db.session)


# @event_router.post("/{event_id}/comment", response_model=CommentEventGet, deprecated=True)
# async def http_comment_event(event_id: int, author_name: str, text: str) -> CommentEventGet:
#     return CommentEventGet.from_orm(CommentEvent(event_id=event_id, db.session, text, author_name))


# @event_router.patch("/{id}/comment", response_model=CommentEventGet, deprecated=True)
# async def http_udpate_comment(comment_id: int, new_text: str) -> CommentEventGet:
#     return CommentEventGet.from_orm(await utils.update_comment_event(comment_id, db.session, new_text))
