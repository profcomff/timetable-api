import datetime

from calendar_backend.models.db import Event, Group, Lecturer, Room
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
