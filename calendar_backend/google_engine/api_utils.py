import googleapiclient.discovery
from sqlalchemy.orm import Session

from .event_from_db import create_google_events_from_db
from .event import Event
from .. import get_settings
from dataclasses import asdict
# async libs for Google API

settings = get_settings()


def create_calendar(service: googleapiclient.discovery.Resource, group: str) -> str:
    """
    Creates a new calendar for timetable on user's account (if not exist)
    returns calendarId
    """
    timetable_calendar = {
        "summary": f"Расписание на физфаке для {group} группы",
        "timeZone": "Europe/Moscow",
    }
    calendars = service.calendarList().list().execute().get("items", [])
    for calendar in calendars:
        if calendar["summary"] == timetable_calendar["summary"]:
            service.calendars().delete(calendarId=calendar["id"]).execute()
    created_calendar = service.calendars().insert(body=timetable_calendar).execute()
    return created_calendar["id"]


def insert_event(service: googleapiclient.discovery.Resource, calendar_id: str, event: dict):
    """
    Inserts an event to calendar.
    API allows inserting events only partially.
    Returns status string with event summary.
    """
    status = service.events().insert(calendarId=calendar_id, body=event).execute()
    return status


async def create_calendar_with_timetable(
    service: googleapiclient.discovery.Resource, group: str, session: Session
) -> None:
    calendar_id: str = create_calendar(service, group)
    events: list[Event] = create_google_events_from_db(group, session=session)
    for event in events:
        status = insert_event(service, calendar_id, event.dict())
        print(status['summary'])
