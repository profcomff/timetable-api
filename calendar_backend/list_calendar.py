import time
from datetime import date as datedatetime
from datetime import datetime, timedelta

import pytz
from fastapi import HTTPException
from icalendar import Calendar, Event, vText
from sqlalchemy.exc import DBAPIError

# import app
from service import get_calendar_service
from settings import Settings
import os

settings = Settings()


def main():
    service = get_calendar_service(44)
    # Call the Calendar API
    print('Getting list of calendars')
    calendars_result = service.calendarList().list().execute()

    calendars = calendars_result.get('items', [])

    if not calendars:
        print('No calendars found.')
    for calendar in calendars:
        summary = calendar['summary']
        id = calendar['id']
        primary = "Primary" if calendar.get('primary') else ""
        print("%s\t%s\t%s" % (summary, id, primary))


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def parse_time_from_db(time: str):
    try:
        return int(time[:(time.index(':'))]), int(time[(time.index(':') + 1):])
    except ValueError as e:
        print(f"The error '{e}' occurred")


async def get_user_calendar(group: str):
    user_calendar = Calendar()
    startday = datedatetime(datedatetime.today().year, datedatetime.today().month, datedatetime.today().day)
    for date in daterange(startday, get_end_of_semester_date()):
        if date.isoweekday() != 7:
            try:
                timetable_of_day = await app.get_timetable_by_group_and_weekday(group, date.isoweekday())
                for i in range(0, len(timetable_of_day)):
                    teacher = "-"
                    place = "-"
                    hour_start, mins_start = parse_time_from_db(timetable_of_day[i]["start"])
                    hour_end, mins_end = parse_time_from_db(timetable_of_day[i]["end"])
                    event = Event()
                    if timetable_of_day[i]["teacher"] is not None:
                        teacher = timetable_of_day[i]["teacher"]
                    event.add("summary", f"{timetable_of_day[i]['subject']}, {teacher}")
                    event.add("dtstart",
                              datetime(date.year, date.month, date.day, hour_start, mins_start, 0, tzinfo=pytz.UTC))
                    event.add("dtend",
                              datetime(date.year, date.month, date.day, hour_end, mins_end, 0, tzinfo=pytz.UTC))
                    if timetable_of_day[i]["place"] is not None:
                        place = timetable_of_day[i]["place"]
                    event["location"] = vText(place)
                    user_calendar.add_component(event)
            except HTTPException as e:
                print(f"The error '{e}' occurred")

        elif date.isoweekday() == 7:
            pass
    return user_calendar


async def create_user_calendar_file(user_calendar: Calendar, group: str):
    try:
        with open(f"{settings.ICS_PATH}{group}", 'wb') as f:
            f.write(user_calendar.to_ical())
            return f"{settings.ICS_PATH}{group}"
    except DBAPIError:
        try:
            os.remove(f"{settings.ICS_PATH}{group}")
        except OSError:
            print(f"The error occurred")
        print(f"The error occurred")


def get_end_of_semester_date():
    if datedatetime.today().month in range(2, 6):
        return datedatetime(datedatetime.today().year, 5, 24)
    elif datetime.today().month in range(9, 13):
        return datedatetime(datedatetime.today().year, 12, 24)
    else:
        return datedatetime(datedatetime.today().year, datedatetime.today().month, datedatetime.today().day)


def check_file_for_creation_date(path_file: str):
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
