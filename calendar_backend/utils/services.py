from datetime import timedelta
from typing import Dict, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from calendar_backend.models import Event, Group, Lecturer, Room
from calendar_backend.routes.models.event import EventRepeatedPost


class EventService:
    """Сервис для работы с логикой создания событий"""

    @classmethod
    async def bulk_create_events(cls, dbsession: Session, events: List[Dict]) -> List[Event]:
        result = []
        for event_dict in events:
            existing_events_query = (
                Event.get_all(session=dbsession)
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
                rooms = [Room.get(room_id, session=dbsession) for room_id in event_dict.pop("room_id", [])]
                lecturers = [
                    Lecturer.get(lecturer_id, session=dbsession) for lecturer_id in event_dict.pop("lecturer_id", [])
                ]
                groups = [Group.get(group_id, session=dbsession) for group_id in event_dict.pop("group_id", [])]
                result.append(
                    Event.create(
                        **event_dict,
                        room=rooms,
                        lecturer=lecturers,
                        group=groups,
                        session=dbsession,
                    )
                )
        dbsession.commit()
        return result

    @classmethod
    async def reproduce_repeating_event(cls, event: EventRepeatedPost) -> List[Dict]:
        if event.repeat_timedelta_days <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Timedelta must be a positive integer")
        if event.repeat_until_ts > event.start_ts + timedelta(days=1095):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due to disk utilization limits, events with duration > 3 years is restricted",
            )
        events = []
        event_dict = event.model_dump()

        rooms = [room_id for room_id in event_dict.pop("room_id", [])]
        lecturers = [lecturer_id for lecturer_id in event_dict.pop("lecturer_id", [])]
        groups = [group_id for group_id in event_dict.pop("group_id", [])]

        repeat_timedelta_days = timedelta(days=event.repeat_timedelta_days)
        cur_start_ts = event_dict["start_ts"]
        cur_end_ts = event_dict["end_ts"]

        while cur_start_ts <= event.repeat_until_ts:
            event_get = {}
            event_get["name"] = event_dict["name"]
            event_get["start_ts"] = cur_start_ts
            event_get["end_ts"] = cur_end_ts
            event_get["room_id"] = rooms
            event_get["lecturer_id"] = lecturers
            event_get["group_id"] = groups
            events.append(event_get)
            cur_start_ts += repeat_timedelta_days
            cur_end_ts += repeat_timedelta_days

        return events
