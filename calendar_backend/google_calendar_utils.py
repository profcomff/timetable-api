import googleapiclient.discovery
from service import get_calendar_service
from dataclasses import dataclass, asdict
from fastapi_sqlalchemy import db
from connect import connect
from settings import Settings
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from db import Timetable
import datetime
from list_calendar import get_end_of_semester_date
# async libraries
import aiohttp
import asyncio
from aiogoogle import Aiogoogle
from aiogoogle.sessions import aiohttp_session


settings = Settings()
session = Session(create_engine(settings.DB_DSN))


@dataclass()
class Event:
    summary: str
    location: str
    description: str
    start: dict
    end: dict
    recurrence: list
    attendees: list
    reminders: dict

def create_google_calendar_event(summary: str,
                                 start_time: str,
                                 end_time: str,
                                 location: str,
                                 description: str) -> dict:
    """
    Creates a dict with a Google calendar params
    """
    end_sem_date = f"{str(get_end_of_semester_date()).replace('-','')}T235900Z"
    event = Event(summary=summary,
                  location=location,
                  description=description,
                  start={
                      'dateTime': start_time,
                      'timeZone': 'Europe/Moscow',
                  },
                  end={
                      'dateTime': end_time,
                      'timeZone': 'Europe/Moscow',
                  },
                  recurrence=[
                     f"RRULE:FREQ=WEEKLY;UNTIL={end_sem_date};INTERVAL=2"
                  ],
                  attendees=[],
                  reminders={'useDefault': False}
                  )
    return asdict(event)


def create_google_events_from_db(group: int) -> list[dict]:
    """
    Creates a timetable for certain group from db timetable.
    Returns list[dict] of events/subjects
    """
    group_subjects = session.query(Timetable).filter(Timetable.group == str(group)).all()
    now = datetime.date.today()
    start_of_week = (now - datetime.timedelta(days=now.weekday())) #start of current week
    is_week_even = start_of_week.isocalendar()[1] % 2 == 0
    time_zone = "+03:00"
    dict_of_subjects = []
    for subject in group_subjects:
        start_date = start_of_week + datetime.timedelta(days=(subject.weekday - 1))
        if is_week_even:
            if subject.even:
                dict_of_subjects.append(create_google_calendar_event(
                    summary=subject.subject,
                    start_time=f"{start_date.isoformat()}T{subject.start}:00{time_zone}",
                    end_time=f"{start_date.isoformat()}T{subject.end}:00{time_zone}",
                    location=subject.place,
                    description=subject.teacher))
        else:
            if subject.odd:
                dict_of_subjects.append(create_google_calendar_event(
                    summary=subject.subject,
                    start_time=f"{start_date.isoformat()}T{subject.start}:00{time_zone}",
                    end_time=f"{start_date.isoformat()}T{subject.end}:00{time_zone}",
                    location=subject.place,
                    description=subject.teacher))
    for subject in group_subjects:
        start_date = start_of_week + datetime.timedelta(days=(7 + subject.weekday - 1))
        if is_week_even:
            if subject.odd:
                dict_of_subjects.append(create_google_calendar_event(
                    summary=subject.subject,
                    start_time=f"{start_date.isoformat()}T{subject.start}:00{time_zone}",
                    end_time=f"{start_date.isoformat()}T{subject.end}:00{time_zone}",
                    location=subject.place,
                    description=subject.teacher))
        else:
            if subject.even:
                dict_of_subjects.append(create_google_calendar_event(
                    summary=subject.subject,
                    start_time=f"{start_date.isoformat()}T{subject.start}:00{time_zone}",
                    end_time=f"{start_date.isoformat()}T{subject.end}:00{time_zone}",
                    location=subject.place,
                    description=subject.teacher))
    return dict_of_subjects


def create_calendar(service, group) -> str:
    """
    Creates a new calendar for timetable on user's account (if not exist)
    returns calendarId
    """
    timetable_calendar = {
        'summary': f'Расписание на физфаке для {group} группы',
        'timeZone': 'Europe/Moscow'
    }
    calendars =  service.calendarList().list().execute().get('items', [])
    for calendar in calendars:
        if calendar['summary'] == timetable_calendar['summary']:
            service.calendars().delete(calendarId=calendar['id']).execute()
    created_calendar = service.calendars().insert(body=timetable_calendar).execute()
    return created_calendar['id']


def insert_event(service: googleapiclient.discovery.Resource,
                 calendar_id: str,
                 event: dict) -> str:
    """
    Inserts an event to calendar.
    API allows inserting events only partially.
    Returns status string with event summary.
    """
    status = service.events().insert(calendarId=calendar_id, body=event).execute()
    return f"Event {status.get('summary')} created"


def create_calendar_with_timetable(service, group):
    calendar_id: str = create_calendar(service, int(group))
    events: list[dict] = create_google_events_from_db(int(group))
    for event in events:
        status = insert_event(service, calendar_id, event)
        print(status)


def create_timetable_calendar_for_user(token: str, group: str) -> None:
    """
    For background tasks
    !NOT TESTED!
    """
    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(json.loads(token), SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    create_calendar_with_timetable(service, int(group))


def test_can_create_calendar_with_timetable():
    service = get_calendar_service(44)
    group = '116' # group is a String type in db
    create_calendar_with_timetable(service, group)


def test_can_create_empty_calendar():
    service = get_calendar_service(44)
    _id = create_calendar(service, '116')
    print('id:', _id)
    calendar = service.calendars().get(calendarId=id).execute()
    print(calendar)


if __name__ == '__main__':
    # test_can_create_google_type_event()
    # create_google_event_from_db(101)
    # test_can_create_timetable_calendar()
    test_can_create_calendar_with_timetable()