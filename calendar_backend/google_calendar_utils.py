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
                  recurrence=[],
                  attendees=[],
                  reminders={'useDefault': False}
                  )
    return asdict(event)


def create_google_event_from_db(group: int) -> dict:
    group_subjects = session.query(Timetable).filter(Timetable.group == str(group)).all()
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    pass

def test_can_create_google_type_event():
    print(create_google_calendar_event('subject', '2015-05-28T09:00:00-07:00', '2015-05-28T17:00:00-07:00'))


def get_event():
    service = get_calendar_service(44)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
    print(events['items'][0])


if __name__ == '__main__':
    # test_can_create_google_type_event()
    # create_google_event_from_db(101)
    get_event()