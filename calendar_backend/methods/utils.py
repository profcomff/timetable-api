import datetime
import os
import random
import string
from typing import Final

import aiofiles
from fastapi import File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from calendar_backend.models.db import (
    Event,
    Group,
    Lecturer,
    Photo,
    Room,
    ApproveStatuses,
)
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
    group: Group, date_start: datetime.date, date_end: datetime.date
) -> list[Event]:
    events_list = []
    for lesson in group.events:
        if lesson.start_ts.date() >= date_start and lesson.end_ts.date() < date_end:
            events_list.append(lesson)
    return events_list


async def get_room_lessons_in_daterange(room: Room, date_start: datetime.date, date_end: datetime.date) -> list[Event]:
    events_list = []
    for lesson in room.events:
        if lesson.start_ts.date() >= date_start and lesson.end_ts.date() < date_end:
            events_list.append(lesson)
    return events_list


async def get_lecturer_lessons_in_daterange(
    lecturer: Lecturer, date_start: datetime.date, date_end: datetime.date
) -> list[Event]:
    events_list = []
    for lesson in lecturer.events:
        if lesson.start_ts.date() >= date_start and lesson.end_ts.date() < date_end:
            events_list.append(lesson)
    return events_list

SUPPORTED_FILE_EXTENSIONS: Final[list[str]] = ['png', 'svg', 'jpg', 'jpeg']

async def upload_lecturer_photo(lecturer_id: int, session: Session, file: UploadFile = File(...)) -> Photo:
    lecturer = Lecturer.get(lecturer_id, session=session)
    random_string = ''.join(random.choice(string.ascii_letters) for _ in range(32))
    ext = file.filename.split('.')[-1]
    if ext not in SUPPORTED_FILE_EXTENSIONS:
        raise HTTPException(status_code=422, detail="Unsupported file extension")
    path = os.path.join(settings.STATIC_PATH, "photo", "lecturer", f"{random_string}.{ext}")
    async with aiofiles.open(path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        approve_status = ApproveStatuses.APPROVED if not settings.REQUIRE_REVIEW_PHOTOS else ApproveStatuses.PENDING
        photo = Photo(
            lecturer_id=lecturer_id,
            link=path,
            approve_status=approve_status,
        )
        session.add(photo)
        session.flush()
        lecturer.avatar_id = lecturer.last_photo.id if lecturer.last_photo else lecturer.avatar_id
        session.commit()
    return photo
