import logging
import os
import time
from datetime import date as date_
from datetime import datetime

import pytz
from icalendar import Calendar, Event, vText
from sqlalchemy.orm import Session

from calendar_backend import get_settings
from . import utils

settings = get_settings()
logger = logging.getLogger(__name__)


async def get_user_calendar(group_number: str, session: Session) -> Calendar:
    """
    Returns event iCalendar object
    """
    logger.debug(f"Getting user calendar (iCal) for group {group_number}")
    group = await utils.get_group_by_name(group_num=group_number, session=session)
    user_calendar = Calendar()
    startday = date_(date_.today().year, date_.today().month, date_.today().day)
    timetable = await utils.get_lessons_by_group_from_date(group, startday)
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
            datetime(
                lesson.start_ts.date().year,
                lesson.start_ts.date().month,
                lesson.start_ts.date().day,
                lesson.start_ts.time().hour,
                lesson.start_ts.time().minute,
                0,
                tzinfo=pytz.UTC,
            ),
        )
        event.add(
            "dtend",
            datetime(
                lesson.end_ts.date().year,
                lesson.end_ts.date().month,
                lesson.end_ts.date().day,
                lesson.end_ts.time().hour,
                lesson.end_ts.time().minute,
                0,
                tzinfo=pytz.UTC,
            ),
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
