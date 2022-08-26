import datetime
import logging

from sqlalchemy.orm import Session

from calendar_backend.settings import get_settings
from calendar_backend.methods.utils import get_lessons_by_group_from_date, get_group_by_id
from calendar_backend.models import Lesson
from .event import create_google_calendar_event, Event

settings = get_settings()
logger = logging.getLogger(__name__)


async def create_google_events_from_db(group_id: int, session: Session) -> list[Event]:
    """
    Creates a timetable for certain group from db.
    Returns list[Event] of events/subjects
    """
    group, _ = await get_group_by_id(group_id, session, False)
    group_lessons: list[Lesson] = await get_lessons_by_group_from_date(group, datetime.date.today())
    list_of_lessons: list[Event] = []
    time_zone = "+03:00"
    logger.debug(f"Getting list of subjects for {group}...")
    for lesson in group_lessons:
        list_of_lessons.append(
            create_google_calendar_event(
                summary=lesson.name,
                start_time=f"{lesson.start_ts.date()}T{lesson.start_ts.time().hour}:{lesson.start_ts.time().minute}:00{time_zone}",
                end_time=f"{lesson.end_ts.date()}T{lesson.end_ts.time().hour}:{lesson.end_ts.time().minute}:00{time_zone}",
                location=str([row.name for row in lesson.room]),
                description=str([f"{row.first_name} {row.middle_name} {row.last_name}" for row in lesson.lecturer]),
            )
        )
        if lesson.start_ts.date() == datetime.date.today() + datetime.timedelta(14):
            break
    return list_of_lessons
