import logging
from datetime import date, datetime, timedelta
from typing import Literal

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi_sqlalchemy import db
from pydantic import TypeAdapter

from calendar_backend.exceptions import NotEnoughCriteria
from calendar_backend.methods import list_calendar
from calendar_backend.models import Event, Group, Lecturer, Room
from calendar_backend.routes.models import EventGet
from calendar_backend.routes.models.event import (
    EventPatch,
    EventPatchName,
    EventPatchResult,
    EventPost,
    EventRepeatedPost,
    GetListEvent,
)
from calendar_backend.settings import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/event", tags=["Event"])


@router.get("/{id}", response_model=EventGet)
async def get_event_by_id(id: int) -> EventGet:
    return EventGet.model_validate(Event.get(id, session=db.session))


async def _get_timetable(start: date, end: date, group_id, lecturer_id, room_id, detail, limit, offset):
    if bool(group_id) + bool(lecturer_id) + bool(room_id) != 1:
        raise NotEnoughCriteria("Exactly one argument group_id, lecturer_id or room_id required")
    events = Event.get_all(session=db.session).filter(
        Event.start_ts >= start,
        Event.end_ts < end,
    )
    if group_id:
        events = events.filter(Event.group.any(Group.id == group_id))
    elif lecturer_id:
        events = events.filter(Event.lecturer.any(Lecturer.id == lecturer_id))
    elif room_id:
        events = events.filter(Event.room.any(Room.id == room_id))
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

    return GetListEvent(items=events, limit=limit, offset=offset, total=cnt).model_dump(exclude=fmt)


@router.get("/", response_model=GetListEvent | None)
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


@router.post("/", response_model=EventGet)
async def create_event(event: EventPost, _=Depends(UnionAuth(scopes=["timetable.event.create"]))) -> EventGet:
    event_dict = event.model_dump()
    rooms = [Room.get(room_id, session=db.session) for room_id in event_dict.pop("room_id", [])]
    lecturers = [Lecturer.get(lecturer_id, session=db.session) for lecturer_id in event_dict.pop("lecturer_id", [])]
    groups = [Group.get(group_id, session=db.session) for group_id in event_dict.pop("group_id", [])]
    event_get = Event.create(
        **event_dict,
        room=rooms,
        lecturer=lecturers,
        group=groups,
        session=db.session,
    )
    db.session.commit()
    return EventGet.model_validate(event_get)


@router.post("/repeating", response_model=list[EventGet])
async def create_repeating_event(
    event: EventRepeatedPost,  # _=Depends(UnionAuth(scopes=["timetable.event.create"]))
) -> list[EventGet]:
    if event.repeat_timedelta_days <= 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": f"Timedelta must be a positive integer"}
        )
    if event.repeat_until_ts > event.start_ts + timedelta(days=1095):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Due to disk utilization limits, events with duration > 3 years is restricted"},
        )
    events = []
    event_dict = event.model_dump()
    rooms = [Room.get(room_id, session=db.session) for room_id in event_dict.pop("room_id", [])]
    lecturers = [Lecturer.get(lecturer_id, session=db.session) for lecturer_id in event_dict.pop("lecturer_id", [])]
    groups = [Group.get(group_id, session=db.session) for group_id in event_dict.pop("group_id", [])]
    repeat_timedelta_days = timedelta(days=event.repeat_timedelta_days)
    cur_start_ts = event_dict["start_ts"]
    cur_end_ts = event_dict["end_ts"]
    while cur_start_ts <= event.repeat_until_ts:
        event_get = Event.create(
            name=event_dict["name"],
            start_ts=cur_start_ts,
            end_ts=cur_end_ts,
            room=rooms,
            lecturer=lecturers,
            group=groups,
            session=db.session,
        )
        events.append(event_get)
        cur_start_ts += repeat_timedelta_days
        cur_end_ts += repeat_timedelta_days
    adapter = TypeAdapter(list[EventGet])
    return adapter.validate_python(events)


@router.post("/bulk", response_model=list[EventGet])
async def create_events(
    events: list[EventPost], _=Depends(UnionAuth(scopes=["timetable.event.create"]))
) -> list[EventGet]:
    result = []
    for event in events:
        event_dict = event.model_dump()
        existing_events_query = (
            Event.get_all(session=db.session)
            .filter(Event.name == event_dict.get("name"))
            .filter(Event.start_ts == event_dict.get("start_ts"))
            .filter(Event.end_ts == event_dict.get("end_ts"))
        )
        is_unique = True
        for existing_event in existing_events_query.all():
            if (
                {column.id for column in existing_event.group} == set(event_dict["group_id"])
                and {column.id for column in existing_event.room} == set(event_dict["room_id"])
                and {column.id for column in existing_event.lecturer} == set(event_dict["lecturer_id"])
            ):
                is_unique = False
        if is_unique:
            rooms = [Room.get(room_id, session=db.session) for room_id in event_dict.pop("room_id", [])]
            lecturers = [
                Lecturer.get(lecturer_id, session=db.session) for lecturer_id in event_dict.pop("lecturer_id", [])
            ]
            groups = [Group.get(group_id, session=db.session) for group_id in event_dict.pop("group_id", [])]
            result.append(
                Event.create(
                    **event_dict,
                    room=rooms,
                    lecturer=lecturers,
                    group=groups,
                    session=db.session,
                )
            )
    db.session.commit()
    adapter = TypeAdapter(list[EventGet])
    return adapter.validate_python(result)


@router.patch("/patch_name", response_model=EventPatchResult, summary="Batch update events by name")
async def patch_event_by_name(
    event_inp: EventPatchName, _=Depends(UnionAuth(scopes=["timetable.event.update"]))
) -> EventPatchResult:
    updated = (
        db.session.query(Event).filter(Event.name == event_inp.old_name).update(values={"name": event_inp.new_name})
    )
    db.session.commit()
    return EventPatchResult(old_name=event_inp.old_name, new_name=event_inp.new_name, updated=updated)


@router.patch("/{id}", response_model=EventGet)
async def patch_event(
    id: int, event_inp: EventPatch, _=Depends(UnionAuth(scopes=["timetable.event.update"]))
) -> EventGet:
    patched = Event.update(id, session=db.session, **event_inp.model_dump(exclude_unset=True))
    db.session.commit()
    return EventGet.model_validate(patched)


@router.delete("/bulk", response_model=None)
async def delete_events(start: date, end: date, _=Depends(UnionAuth(scopes=["timetable.event.delete"]))) -> None:
    db.session.query(Event).filter(Event.start_ts >= start, Event.end_ts < end).update(values={"is_deleted": True})
    db.session.commit()


@router.delete("/{id}", response_model=None)
async def delete_event(id: int, _=Depends(UnionAuth(scopes=["timetable.event.delete"]))) -> None:
    Event.delete(id, session=db.session)
    db.session.commit()
