import datetime
from settings import Settings
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from db import Timetable
from event import create_google_calendar_event


settings = Settings()
session = Session(create_engine(settings.DB_DSN))


def create_google_events_from_db(group: str) -> list[dict]:
    """
    Creates a timetable for certain group from db timetable.
    Returns list[dict] of events/subjects
    """
    group_subjects = session.query(Timetable).filter(Timetable.group == group).all()
    now = datetime.date.today()
    start_of_week = (now - datetime.timedelta(days=now.weekday()))  # start of current week
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
