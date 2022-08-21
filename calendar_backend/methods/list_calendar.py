import asyncio
import logging
import os
import time
from datetime import date as date_
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import FileResponse

import pytz
from icalendar import Calendar, Event, vText
from sqlalchemy.orm import Session

from calendar_backend import get_settings
from . import utils

settings = get_settings()
logger = logging.getLogger(__name__)


async def get_user_calendar(group_num: str, session: Session, start_date: date_, end_date: date_) -> Calendar:
    """
    Returns event iCalendar object
    """
    logger.debug(f"Getting user calendar (iCal) for group {group_num}")
    group, _ = (await utils.get_list_groups(session, group_num))
    user_calendar = Calendar()
    timetable = await utils.get_group_lessons_in_daterange(group, start_date, end_date)
    for lesson in timetable:
        teacher = (
            f"{lesson.lecturer.first_name} {lesson.lecturer.middle_name} {lesson.lecturer.last_name}"
            if lesson.lecturer
            else "-"
        )
        place = f"{lesson.room.name}" if lesson.room else "-"
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
        with open(f"{settings.ICS_PATH}/{group}", "wb") as f:
            f.write(user_calendar.to_ical())
        return f"{settings.ICS_PATH}/{group}"
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
        return date_(
            date_.today().year,
            date_.today().month,
            date_.today().day,
        )


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


async def create_ics(group_num: str, start: datetime.date, end: datetime.date, session: Session):
    if check_file_for_creation_date(f"{settings.ICS_PATH}/{group_num}") is False:
        logger.debug(f"Calendar for group '{group_num}' found in cache")
        return FileResponse(f"{settings.ICS_PATH}/{group_num}")
    else:
        async with asyncio.Lock():
            logger.debug("Getting user calendar...")
            user_calendar = await get_user_calendar(group_num, session=session, start_date=start, end_date=end)
            if not user_calendar:
                logger.info(f"Failed to create .ics file for group {group_num} (500)")
                raise HTTPException(status_code=500, detail="Failed to create .ics file")
            logger.debug("Creating .ics file OK")
            return FileResponse(await create_user_calendar_file(user_calendar, group_num))
