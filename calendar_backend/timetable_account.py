import json
import time
import os
import googleapiclient.discovery
from service import get_calendar_service, get_calendar_service_from_token
from google_api_utils import *
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from db import Timetable, Credentials
from settings import Settings


settings = Settings()
session = Session(create_engine(settings.DB_DSN))


def get_all_groups_from_db():
    timetable = session.query(Timetable).all()
    groups = set()
    for row in timetable:
        groups.add(row.group)
    return groups


def create_timetable_for_all_groups():
    service = get_calendar_service(id=find_timetable_account_id())
    groups = get_all_groups_from_db()
    for group in groups:
        calendars = service.calendarList().list().execute().get('items', [])
        is_inserted = False
        for calendar in calendars:
            if calendar['summary'] == f'Расписание на физфаке для {group} группы':
                is_inserted = True
                break
        if is_inserted:
            print(f"calendar for {group} already exists")
        else:
            print(f'crating calendar for {group}....\n')
            create_calendar_with_timetable(service, group)
            print()
            time.sleep(10)


def find_timetable_account_id() -> int:
    """
    Returns an ID of Credentials row with timetable account for fewer get_calendar_service() function.
    """
    emails = session.query(Credentials).filter(Credentials.email == 'profcomff.timetable@gmail.com').all()
    if len(emails):
        if os.path.exists('../timetable_token.json'):
            return emails[0].id
        else:
            with open('../timetable_token.json', 'w') as token_file:
                token_file.write(emails[0].token)
            return emails[0].id
    else:
        print('Token for timetable account not found. Please register it manually')
        return 0


def get_timetable_account_service() -> googleapiclient.discovery.Resource:
    if os.path.exists('../timetable_token.json'):
        print('нашел, вссё окей')
        with open('../timetable_token.json', 'r') as token_file:
            token = token_file.read()
        return get_calendar_service_from_token(token)
    else:
        print('не нашел бля')
        return get_calendar_service(find_timetable_account_id())


if __name__ == "__main__":
    create_timetable_for_all_groups()
    # print(get_all_groups_from_db(), len(get_all_groups_from_db()))
    # print(find_timetable_account_id())
