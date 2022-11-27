import logging
from datetime import date, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as

import calendar_backend.methods.utils
from calendar_backend.exceptions import NotEnoughCriteria
from calendar_backend.methods import auth, list_calendar
from calendar_backend.models import Room, Lecturer, Event, EventsLecturers, EventsRooms, Group
from calendar_backend.routes.models.event import (
    EventGet,
    EventPatch,
    EventPost,
    GetListEvent,
)
from calendar_backend.settings import get_settings

event_router = APIRouter(prefix="/timetable/event", tags=["Event"])
settings = get_settings()
logger = logging.getLogger(__name__)


@event_router.get("/{id}", response_model=EventGet)
async def get_event_by_id(id: int) -> EventGet:
    return EventGet.from_orm(Event.get(id, session=db.session))


async def _get_timetable(start: date, end: date, group_id, lecturer_id, room_id, detail, limit, offset):
    if bool(group_id) + bool(lecturer_id) + bool(room_id) != 1:
        raise NotEnoughCriteria(f"Exactly one argument group_id, lecturer_id or room_id required")
    events = Event.get_all(session=db.session).filter(
        Event.start_ts >= start,
        Event.end_ts < end,
    )
    if group_id:
        events = events.filter(Event.group_id == group_id)
    elif lecturer_id:
        ids_ = EventsLecturers.get_all(session=db.session).filter(EventsLecturers.lecturer_id == lecturer_id).all()
        events = events.filter(Event.id.in_(row.event_id for row in ids_))
    elif room_id:
        ids_ = EventsRooms.get_all(session=db.session).filter(EventsRooms.room_id == room_id).all()
        events = events.filter(Event.id.in_(row.event_id for row in ids_))
    cnt = events.count()
    if limit:
        events = events.order_by(Event.start_ts).limit(limit).offset(offset).all()
    else:
        events = events.order_by(Event.start_ts).offset(offset).all()

    fmt = {}
    if detail and "comment" not in detail:
        fmt["comments"] = ...
    if detail and "description" not in detail:
        fmt["lecturer"] = [
            {
                "avatar_id": ...,
                "description": ...,
                "is_deleted": ...,
            }
        ]

    return GetListEvent(items=events, limit=limit, offset=offset, total=cnt).dict(exclude=fmt)


@event_router.get("/", response_model=GetListEvent | None)
async def get_events(
    start: date | None = Query(default=None, description="Default: Today"),
    end: date | None = Query(default=None, description="Default: Tomorrow"),
    group_id: int | None = None,
    lecturer_id: int | None = None,
    room_id: int | None = None,
    detail: list[Literal["comment", "description", ""]] | None = Query(None),
    format: Literal["json", "ics"] = "json",
    limit: int = 100,
    offset: int = 0,
) -> GetListEvent | FileResponse:
    start = start or date.today()
    end = end or date.today() + timedelta(days=1)
    fmt_cases = {
        "ics": lambda: list_calendar.create_ics(group_id, start, end, db.session),
        "json": lambda: _get_timetable(start, end, group_id, lecturer_id, room_id, detail, limit, offset),
    }
    return await fmt_cases[format]()


@event_router.post("/", response_model=EventGet)
async def create_event(event: EventPost, _: auth.User = Depends(auth.get_current_user)) -> EventGet:
    event_dict = event.dict()
    rooms = [Room.get(room_id, session=db.session) for room_id in event_dict.pop("room_id", [])]
    lecturers = [Lecturer.get(lecturer_id, session=db.session) for lecturer_id in event_dict.pop("lecturer_id", [])]
    group = Group.get(event.group_id, session=db.session)
    return EventGet.from_orm(
        Event.create(
            **event_dict,
            room=rooms,
            lecturer=lecturers,
            group=group,
            session=db.session,
        )
    )


@event_router.post("/bulk", response_model=list[EventGet])
async def create_events(events: list[EventPost], _: auth.User = Depends(auth.get_current_user)) -> list[EventGet]:
    result = []
    for event in events:
        event_dict = event.dict()
        rooms = [Room.get(room_id, session=db.session) for room_id in event_dict.pop("room_id", [])]
        lecturers = [Lecturer.get(lecturer_id, session=db.session) for lecturer_id in event_dict.pop("lecturer_id", [])]
        group = Group.get(event.group_id, session=db.session)
        result.append(Event.create(
            **event_dict,
            room=rooms,
            lecturer=lecturers,
            group=group,
            session=db.session,
        ))
        return parse_obj_as(list[EventGet], result)


@event_router.patch("/{id}", response_model=EventGet)
async def patch_event(id: int, event_inp: EventPatch, _: auth.User = Depends(auth.get_current_user)) -> EventGet:
    return EventGet.from_orm(Event.update(id, session=db.session, **event_inp.dict(exclude_unset=True)))


@event_router.delete("/{id}", response_model=None)
async def delete_event(id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    Event.delete(id, session=db.session)


@event_router.delete("/bulk", response_model=None)
async def delete_events(start: date, end: date, _: auth.User = Depends(auth.get_current_user)) -> None:
    events = Event.get_all(session=db.session).filter(
        Event.start_ts >= start,
        Event.end_ts < end,
    ).all()
    for event in events:
        Event.delete(event.id, session=db.session)
