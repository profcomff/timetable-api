import datetime
import os
import random
import string
from typing import Coroutine
import logging
import aiofiles
from fastapi import File, UploadFile
from sqlalchemy.orm import Session

from calendar_backend.models.db import Event, Group, Lecturer, Photo, Room, EventsRooms, EventsLecturers
from calendar_backend.settings import get_settings


settings = get_settings()


def get_end_of_semester_date() -> datetime.date:
    """
    Returns last day of the semester
    """
    if datetime.date.today().month in range(2, 6):
        return datetime.date(datetime.date.today().year, 5, 24)
    elif datetime.datetime.today().month in range(9, 13):
        return datetime.date(datetime.date.today().year, 12, 24)
    else:
        return datetime.date.today()

async def get_lessons_by_group_from_date(group: Group, date: datetime.date) -> list[Event]:
    events = group.events
    events_from_date: list[Event] = []
    for lesson in events:
        if lesson.start_ts.date() >= date:
            events_from_date.append(lesson)
    return events_from_date


async def get_group_lessons_in_daterange(
    group: Group, date_start: datetime.date, date_end: datetime.date, session: Session
) -> list[Event]:
    events_list = []
    events = Event.get_all(session=session).filter(Event.group_id == group.id).all()
    for lesson in events:
        if lesson.start_ts.date() >= date_start and lesson.end_ts.date() < date_end:
            events_list.append(lesson)
    return events_list


async def get_room_lessons_in_daterange(room: Room, date_start: datetime.date, date_end: datetime.date, session: Session) -> list[Event]:
    events_list = []
    events_ids = EventsRooms.get_all(session=session).filter(EventsRooms.room_id == room.id).all()
    events = [Event.get(row, session=session) for row in events_ids]
    for lesson in events:
        if lesson.start_ts.date() >= date_start and lesson.end_ts.date() < date_end:
            events_list.append(lesson)
    return events_list


async def get_lecturer_lessons_in_daterange(
    lecturer: Lecturer, date_start: datetime.date, date_end: datetime.date, session: Session
) -> list[Event]:
    events_list = []
    events_ids = EventsLecturers.get_all(session=session).filter(EventsRooms.room_id == lecturer.id).all()
    events = [Event.get(row, session=session) for row in events_ids]
    for lesson in events:
        if lesson.start_ts.date() >= date_start and lesson.end_ts.date() < date_end:
            events_list.append(lesson)
    return events_list

async def create_group_list(session: Session) -> list:
    groups: list[Group] = session.query(Group).filter().all()
    return [f"{row.number}, {row.name}" if row.name else f"{row.number}" for row in groups]

async def check_group_existing(session: Session, group_num: str) -> bool:
    if session.query(Group).filter(Group.number == group_num).one_or_none():
        return True
    return False

async def upload_lecturer_photo(lecturer_id: int, session: Session, file: UploadFile = File(...)) -> Photo:
    random_string = ''.join(random.choice(string.ascii_letters) for i in range(32))
    ext = file.filename.split('.')[-1]
    path = os.path.join(settings.PHOTO_LECTURER_PATH, f"{random_string}.{ext}")
    async with aiofiles.open(path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        photo = Photo(lecturer_id=lecturer_id, link=path)
        session.add(photo)
        session.flush()
    return photo

async def set_lecturer_avatar(lecturer_id: int, photo_id: int, session: Session) -> Lecturer:
    lecturer = Lecturer.get(lecturer_id, session=session)
    if photo_id in [row.id for row in lecturer.photos]:
        photo = Photo.get(photo_id, session=session)
        lecturer.avatar_id = photo.id
        lecturer.avatar_link = photo.link
        return lecturer
