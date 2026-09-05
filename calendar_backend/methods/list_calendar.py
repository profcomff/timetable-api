import asyncio
import logging
import os
import time
from datetime import date as date_
from datetime import datetime
from typing import List

import pytz
from fastapi import File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from icalendar import Calendar, Event, vText
from sqlalchemy.orm import Session

from calendar_backend.models import Event as DB_Event
from calendar_backend.models import Group, Lecturer, Room
from calendar_backend.settings import get_settings

from . import utils


settings = get_settings()
logger = logging.getLogger(__name__)


def _get_list_from_ical_obj(element, field: str) -> List:
    items = element.get(field)
    if not items:
        return []
    elif isinstance(items, list):
        return [int(i) for i in items]
    elif "," in (str_items := str(items)):
        return [int(i) for i in items.split(",")]
    else:
        return [int(items)]


async def create_event_from_icalendar(dbsession: Session, file: UploadFile = File(...)) -> List:
    extension = file.filename.split(".")[-1]
    available_exts = ["ical", "ics"]
    if extension not in available_exts:
        raise HTTPException(status_code=422, detail="Не поддерживаемый фармат файла!")

    raw_file: bytes = file.read()
    str_file: str = raw_file.decode("utf-8")
    cal_obj = Calendar.from_ical(str_file)
    events = []
    result = []
    for element in cal_obj.walk():
        data = {}
        data["name"] = element.get("summary")
        data["start_ts"] = element.get("dtstart")
        data["end_ts"] = element.get("dtend")
        group_ids_field, lecturer_ids_field, room_ids_field = "X-FF-GROUP-IDS", "X-FF-LECTURER-IDS", "X-FF-ROOM-IDS"
        data["group_ids"] = _get_list_from_ical_obj(element, group_ids_field)
        data["lecturer_ids"] = _get_list_from_ical_obj(element, lecturer_ids_field)
        data["room_ids"] = _get_list_from_ical_obj(element, room_ids_field)
        # решено, что group_id обязателен
        if not data.get("group_ids"):
            raise HTTPException(status_code=403, detail="Невозможно создать событие без группы!")
        events.append(data)

    for data in events:
        existing_events_query = (
            DB_Event.get_all(session=dbsession)
            .filter(DB_Event.name == data.get("name"))
            .filter(DB_Event.start_ts == data.get("start_ts"))
            .filter(DB_Event.end_ts == data.get("end_ts"))
        )
        is_unique = True
        for existing_event in existing_events_query.all():
            if (
                {column.id for column in existing_event.group} == set(data["group_id"])
                and {column.id for column in existing_event.room} == set(data["room_id"])
                and {column.id for column in existing_event.lecturer} == set(data["lecturer_id"])
            ):
                is_unique = False

        if is_unique:
            rooms = [Room.get(room_id, session=dbsession) for room_id in data.pop("room_id", [])]
            lecturers = [Lecturer.get(lecturer_id, session=dbsession) for lecturer_id in data.pop("lecturer_id", [])]
            groups = [Group.get(group_id, session=dbsession) for group_id in data.pop("group_id", [])]
            result.append(
                DB_Event.create(
                    **data,
                    room=rooms,
                    lecturer=lecturers,
                    group=groups,
                    session=dbsession,
                )
            )
    dbsession.commit()
    return result


async def get_user_calendar(group_id: int, session: Session, start_date: date_, end_date: date_) -> Calendar:
    """
    Returns event iCalendar object
    """
    logger.debug(f"Getting user calendar (iCal) for group {group_id}")
    group = Group.get(group_id, session=session)
    user_calendar = Calendar()
    timetable = await utils.get_group_lessons_in_daterange(group, start_date, end_date)
    for lesson in timetable:
        teacher = (
            str([f"{row.first_name} {row.middle_name} {row.last_name}" for row in lesson.lecturer])
            if lesson.lecturer
            else "-"
        )
        place = str([row.name for row in lesson.room]) if lesson.room else "-"
        event = Event()
        event.add("summary", f"{lesson.name}, {teacher}")
        event.add(
            "dtstart",
            lesson.start_ts.replace(tzinfo=pytz.UTC),
        )
        event.add(
            "dtend",
            lesson.end_ts.replace(tzinfo=pytz.UTC),
        )
        event["location"] = vText(place)
        user_calendar.add_component(event)
    return user_calendar


async def create_user_calendar_file(user_calendar: Calendar, group: str) -> str:
    """
    Creating .ics file from iCalendar object
    """
    logger.debug(f"Creating .ics file from iCalendar {user_calendar.name}")
    try:
        with open(f"{settings.STATIC_PATH}/cache/{group}", "wb") as f:
            f.write(user_calendar.to_ical())
        return f"{settings.STATIC_PATH}/cache/{group}"
    except OSError as e:
        logger.info(f"The error {e} occurred")


def get_end_of_semester_date() -> date_:
    """
    Returns last day of the semester
    """
    if date_.today().month in range(2, 6):
        return date_(date_.today().year, 5, 24)
    elif datetime.today().month in range(9, 13):
        return date_(date_.today().year, 12, 24)
    else:
        return date_.today()


def check_file_for_creation_date(path_file: str) -> bool:
    """
    Checks that the file was created no more than one day ago
    True: if the file needs to be recreated/created
    False: if file exists and created last day
    """
    logger.debug(f"Checking file {path_file} for creation date/existing...")
    if os.path.exists(path_file):
        try:
            c_time = os.path.getctime(path_file)
            date_time_of_creation = datetime.strptime(time.ctime(c_time), "%c")
            if (datetime.today() - date_time_of_creation).days >= 1:
                return True
            else:
                return False
        except OSError as e:
            logger.info(f"The error '{e}' occurred")
            return False
    else:
        return True


async def create_ics(group_id: int, start: datetime.date, end: datetime.date, session: Session):
    if check_file_for_creation_date(f"{settings.STATIC_PATH}/cache/{group_id}") is False:
        logger.debug(f"Calendar for group '{group_id}' found in cache")
        return FileResponse(f"{settings.STATIC_PATH}/cache/{group_id}")
    else:
        async with asyncio.Lock():
            logger.debug("Getting user calendar...")
            user_calendar = await get_user_calendar(group_id, session=session, start_date=start, end_date=end)
            if not user_calendar:
                logger.info(f"Failed to create .ics file for group {group_id} (500)")
                raise HTTPException(status_code=500, detail="Failed to create .ics file")
            logger.debug("Creating .ics file OK")
            return FileResponse(await create_user_calendar_file(user_calendar, group_id))
