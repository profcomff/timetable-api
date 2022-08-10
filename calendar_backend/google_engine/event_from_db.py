import datetime

from sqlalchemy.orm import Session

from ..models import Timetable
from .. import get_settings
from .event import create_google_calendar_event, Event
import logging

settings = get_settings()
logger = logging.getLogger(__name__)


def create_google_events_from_db(group: str, session: Session) -> list[Event]:
    """
    Creates a timetable for certain group from db timetable.
    Returns list[Event] of events/subjects
    """
    group_subjects = session.query(Timetable).filter(Timetable.group == group).all()
    now = datetime.date.today()
    start_of_week = now - datetime.timedelta(days=now.weekday())  # start of current week
    is_week_even = start_of_week.isocalendar()[1] % 2 == 0
    time_zone = "+03:00"
    list_of_subjects = []
    logger.debug(f"Getting list of subjects for {group}...")
    for subject in group_subjects:
        start_date = start_of_week + datetime.timedelta(days=(subject.weekday - 1))
        if is_week_even:
            if subject.even:
                list_of_subjects.append(
                    create_google_calendar_event(
                        summary=subject.subject,
                        start_time=f"{start_date.isoformat()}T{subject.start}:00{time_zone}",
                        end_time=f"{start_date.isoformat()}T{subject.end}:00{time_zone}",
                        location=subject.place,
                        description=subject.teacher,
                    )
                )
        else:
            if subject.odd:
                list_of_subjects.append(
                    create_google_calendar_event(
                        summary=subject.subject,
                        start_time=f"{start_date.isoformat()}T{subject.start}:00{time_zone}",
                        end_time=f"{start_date.isoformat()}T{subject.end}:00{time_zone}",
                        location=subject.place,
                        description=subject.teacher,
                    )
                )
    for subject in group_subjects:
        start_date = start_of_week + datetime.timedelta(days=(7 + subject.weekday - 1))
        if is_week_even:
            if subject.odd:
                list_of_subjects.append(
                    create_google_calendar_event(
                        summary=subject.subject,
                        start_time=f"{start_date.isoformat()}T{subject.start}:00{time_zone}",
                        end_time=f"{start_date.isoformat()}T{subject.end}:00{time_zone}",
                        location=subject.place,
                        description=subject.teacher,
                    )
                )
        else:
            if subject.even:
                list_of_subjects.append(
                    create_google_calendar_event(
                        summary=subject.subject,
                        start_time=f"{start_date.isoformat()}T{subject.start}:00{time_zone}",
                        end_time=f"{start_date.isoformat()}T{subject.end}:00{time_zone}",
                        location=subject.place,
                        description=subject.teacher,
                    )
                )
    return list_of_subjects
