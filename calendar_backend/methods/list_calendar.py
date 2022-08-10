import os
import time
from datetime import date as date_
from datetime import datetime, timedelta
from typing import Iterator

import pytz
import logging
from icalendar import Calendar, Event, vText
from sqlalchemy.orm import Session

from calendar_backend import get_settings
from calendar_backend.methods import getters

settings = get_settings()
logger = logging.getLogger(__name__)


def daterange(start_date: date_, end_date: date_) -> Iterator[date_]:
    """
    Date iterator
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def parse_time_from_db(time: str) -> tuple[int, int]:
    """
    Parsing time from db to datetime format
    """
    logger.debug("Parsing time from db...")
    try:
        return int(time[: (time.index(":"))]), int(time[(time.index(":") + 1) :])
    except ValueError as e:
        logger.info(f"The error '{e}' occurred")


async def get_user_calendar(group: str, session: Session) -> Calendar:
    """
    Returns event iCalendar object
    """
    logger.debug(f"Getting user calendar (iCal) for group {group}")
    user_calendar = Calendar()
    startday = date_(date_.today().year, date_.today().month, date_.today().day)
    for date in daterange(startday, get_end_of_semester_date()):
        is_week_even = date.isocalendar()[1] % 2 == 0
        if date.isoweekday() != 7:
            timetable_of_day = await getters.get_timetable_by_group_and_weekday(
                group, date.isoweekday(), session=session
            )
            for subject in timetable_of_day:
                if (is_week_even and subject.odd) or (not is_week_even and subject.even):
                    continue
                (
                    hour_start,
                    mins_start,
                ) = parse_time_from_db(subject.start)
                hour_end, mins_end = parse_time_from_db(subject.end)
                event = Event()
                teacher = subject.teacher or "-"
                event.add("summary", f"{subject.subject}, {teacher}")
                event.add(
                    "dtstart",
                    datetime(
                        date.year,
                        date.month,
                        date.day,
                        hour_start,
                        mins_start,
                        0,
                        tzinfo=pytz.UTC,
                    ),
                )
                event.add(
                    "dtend",
                    datetime(
                        date.year,
                        date.month,
                        date.day,
                        hour_end,
                        mins_end,
                        0,
                        tzinfo=pytz.UTC,
                    ),
                )
                place = subject.place or "-"
                event["location"] = vText(place)
                user_calendar.add_component(event)
        elif date.isoweekday() == 7:
            continue
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