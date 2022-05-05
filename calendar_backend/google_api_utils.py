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