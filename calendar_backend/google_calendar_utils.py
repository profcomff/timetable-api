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
from list_calendar import get_end_of_semester_date, get_start_of_semester_date


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
                                 location='physics dept',
                                 description='a subject for students') -> dict:
    """
    Creates a dict with a Google calendar params
    """
    start_sem_date = get_start_of_semester_date()
    end_sem_date = get_end_of_semester_date()
    time_zone = "+03:00"
    event_start_time = f"{start_sem_date}:{start_time}{time_zone}"
    event_end_time = f"{start_sem_date}:{end_time}{time_zone}"
    event = Event(summary=summary,
                  location=location,
                  description=description,
                  start={
                      'dateTime': event_start_time,
                      'timeZone': 'Europe/Moscow',
                  },
                  end={
                      'dateTime': event_end_time,
                      'timeZone': 'Europe/Moscow',
                  },
                  recurrence=[
                     # f"RRULE:FREQ=WEEKLY;UNTIL={end_sem_date};INTERVAL=2"
                  ],
                  attendees=[],
                  reminders={'useDefault': False}
                  )
    return asdict(event)


def create_google_event_from_db(group: int) -> dict:
    group_subjects = session.query(Timetable).filter(Timetable.group == str(group)).all()
    subject = group_subjects[4]
    teacher = subject.teacher
    summary = f"{subject.subject}\n{teacher}"
    start_time = f"{subject.start}:00.000"
    end_time = f"{subject.end}:00.000"
    return create_google_calendar_event(summary, start_time, end_time)


def create_timetable_calendar(service) -> str:
    """
    Creates a new calendar for timetable on user's account (if not exist)
    returns calendarId
    """
    timetable_calendar = {
        'summary': 'Расписание на физфаке',
        'timeZone': 'Europe/Moscow'
    }
    calendars =  service.calendarList().list().execute().get('items', [])
    for calendar in calendars:
        if calendar['summary'] == timetable_calendar['summary']:
            return calendar['id']
    created_calendar = service.calendars().insert(body=timetable_calendar).execute()
    return created_calendar['id']

def get_event():
    service = get_calendar_service(44)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
    print(events['items'][0])

def insert_event(event: dict):
    service = get_calendar_service(44)


def test_can_create_google_type_event():
    print(create_google_calendar_event('subject', '2015-05-28T09:00:00-07:00', '2015-05-28T17:00:00-07:00'))


def test_can_create_timetable_calendar():
    service = get_calendar_service(44)
    id = create_timetable_calendar(service)
    print('id:', id)
    calendar = service.calendars().get(calendarId=id).execute()
    events = service.events().list(calendarId=id).execute()
    print(events)
    print(calendar)



if __name__ == '__main__':
    # test_can_create_google_type_event()
    # create_google_event_from_db(101)
    # get_event()
    # print(datetime.datetime.utcnow().isoformat())
    # print(datetime.date.weekday(datetime.date.today()))
    # print(get_end_of_semester_date(), get_start_of_semester_date())
    test_can_create_timetable_calendar()