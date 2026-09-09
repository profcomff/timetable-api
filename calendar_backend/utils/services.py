from typing import List, Dict

from sqlalchemy.orm import Session
from calendar_backend.models import Event, Group, Lecturer, Room

class EventService:
    """Сервис для работы с логикой создания событий"""


    @classmethod
    async def bulk_create_events(cls, db: Session, events: List[Dict]) -> List[Event]:
        result = []
        for event_dict in events:
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
        return result

    @classmethod
    async def create_repeating_event(cls):
        pass


