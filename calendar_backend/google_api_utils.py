import googleapiclient.discovery
from settings import Settings
from db_event_create import *
from googleapiclient.errors import HttpError
from typing import Optional
settings = Settings()


def create_calendar(service: googleapiclient.discovery.Resource, group: str) -> str:
    """
    Creates a new calendar for timetable on user's account (if not exist)
    returns calendarId
    """
    timetable_calendar = {
        'summary': f'Расписание на физфаке для {group} группы',
        'timeZone': 'Europe/Moscow'
    }  
    calendars = service.calendarList().list().execute().get('items', [])
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
    return f"Event {status.get('summary')} inserted"


def create_calendar_with_timetable(service: googleapiclient.discovery.Resource, group: str):
    calendar_id: str = create_calendar(service, group)
    events: list[dict] = create_google_events_from_db(group)
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
    create_calendar_with_timetable(service, group)


async def copy_timetable_to_user_calendar_list(user_service: googleapiclient.discovery.Resource,
                                         user_group: str,
                                         timetable_service: googleapiclient.discovery.Resource):
    """Creates a copy of timetable in user calendar list with read-only access type."""
    pass
