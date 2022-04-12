from datetime import date as datedatetime
from datetime import datetime, timedelta

import pytz
from fastapi import HTTPException
from icalendar import Calendar, Event, vText
import app
from service import get_calendar_service
from settings import Settings

settings = Settings()


def main():
    service = get_calendar_service()
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
            except HTTPException as e:
                print(f"The error '{e}' occurred")
            for i in range(0, len(timetable_of_day)):
                hour_start, mins_start = parse_time_from_db(timetable_of_day[i]["start"])
                hour_end, mins_end = parse_time_from_db(timetable_of_day[i]["end"])
                event = Event()
                if timetable_of_day[i]["teacher"] is not None:
                    teacher = timetable_of_day[i]["teacher"]
                elif timetable_of_day[i]["teacher"] is None:
                    teacher = "-"
                event.add("summary", f"{timetable_of_day[i]['subject']}, {teacher}")
                event.add("dtstart",
                          datetime(date.year, date.month, date.day, hour_start, hour_end, 0, tzinfo=pytz.UTC))
                event.add("dtend", datetime(date.year, date.month, date.day, hour_end, mins_end, 0, tzinfo=pytz.UTC))
                if timetable_of_day[i]["place"] is not None:
                    place = timetable_of_day[i]["place"]
                elif timetable_of_day[i]["place"] is None:
                    place = "-"
                event["location"] = vText(place)
                user_calendar.add_component(event)
        elif date.isoweekday() == 7:
            pass
    return user_calendar


async def create_user_calendar_file(user_calendar: Calendar):
    try:
        f = open(settings.ICS_PATH, 'wb')
        try:
            f.write(user_calendar.to_ical())
            print("okay")
            return settings.ICS_PATH
        except OSError as e:
            print(f"The error '{e}' occurred")
        finally:
            f.close()
    except OSError as e:
        print(f"The error '{e}' occurred")


def get_end_of_semester_date():
    if datedatetime.today().month in range(2, 6):
        return datedatetime(datedatetime.today().year, 5, 24)
    elif datetime.today().month in range(9, 13):
        return datedatetime(datedatetime.today().year, 12, 24)
