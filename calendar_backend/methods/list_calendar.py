import os
import time
from datetime import date as date_
from datetime import datetime, timedelta
from typing import Iterator, Tuple

import pytz
from fastapi import HTTPException
from icalendar import Calendar, Event, vText
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from calendar_backend.methods import getters
from calendar_backend.settings import get_settings

settings = get_settings()


def daterange(start_date, end_date) -> Iterator:
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def parse_time_from_db(time: str) -> tuple[int, int]:
    try:
        return int(time[: (time.index(":"))]), int(time[(time.index(":") + 1) :])
    except ValueError as e:
        print(f"The error '{e}' occurred")


async def get_user_calendar(group: str, session: Session) -> Calendar:
    user_calendar = Calendar()
    startday = date_(
        date_.today().year, date_.today().month, date_.today().day
    )
    for date in daterange(startday, get_end_of_semester_date()):
        if date.isoweekday() != 7:
            try:
                timetable_of_day = await getters.get_timetable_by_group_and_weekday(
                    group, date.isoweekday(), session=session
                )
            except HTTPException as e:
                print(f"The error '{e}' occurred")
            for i in range(0, len(timetable_of_day)):
                hour_start, mins_start = parse_time_from_db(
                    timetable_of_day[i]["start"]
                )
                hour_end, mins_end = parse_time_from_db(timetable_of_day[i]["end"])
                event = Event()
                if timetable_of_day[i]["teacher"] is not None:
                    teacher = timetable_of_day[i]["teacher"]
                elif timetable_of_day[i]["teacher"] is None:
                    teacher = "-"
                event.add("summary", f"{timetable_of_day[i]['subject']}, {teacher}")
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
                if timetable_of_day[i]["place"] is not None:
                    place = timetable_of_day[i]["place"]
                elif timetable_of_day[i]["place"] is None:
                    place = "-"
                event["location"] = vText(place)
                user_calendar.add_component(event)
        elif date.isoweekday() == 7:
            pass
    return user_calendar


async def create_user_calendar_file(user_calendar: Calendar, group: str) -> str:
    try:
        with open(f"{settings.ICS_PATH}{group}", "wb") as f:
            f.write(user_calendar.to_ical())
            return f"{settings.ICS_PATH}{group}"
    except DBAPIError:
        try:
            os.remove(f"{settings.ICS_PATH}{group}")
        except OSError:
            print(f"The error occurred")
        print(f"The error occurred")


def get_end_of_semester_date() -> date_:
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
    if os.path.exists(path_file):
        try:
            c_time = os.path.getctime(path_file)
            date_time_of_creation = datetime.strptime(time.ctime(c_time), "%c")
            if (datetime.today() - date_time_of_creation).days >= 1:
                return True
            else:
                return False
        except OSError as e:
            print(f"The error '{e}' occurred")
    else:
        return True
