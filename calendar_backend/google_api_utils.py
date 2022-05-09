import json

import googleapiclient.discovery
from settings import Settings
from db_event_create import *
from googleapiclient.errors import HttpError
from typing import Optional
# async libs for Google API
import asyncio
from aiogoogle import Aiogoogle


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


async def copy_timetable_to_user_calendar_list(timetable_service: googleapiclient.discovery.Resource,
                                               user_group: str,
                                               user_email: str) -> str:
    """Creates a copy of timetable in user calendar list with read-only access type."""
    timetable_id = ''
    rule = {
        'scope': {
            'type': "user",
            'value': user_email,
        },
        'role': "reader"
    }
    try:
        timetable_list = timetable_service.calendarList().list().execute().get('items', [])
        is_found: bool = False
        for timetable in timetable_list:
            if timetable['summary'] == f'Расписание на физфаке для {user_group} группы':
                timetable_id = timetable['id']
                is_found = True
                break
        if is_found:
            created_rule = timetable_service.acl().insert(calendarId=timetable_id, body=rule).execute()
            return created_rule['id']
        else:
            return 'not found'
    except googleapiclient.errors.Error:
        print('error copying calendar')
