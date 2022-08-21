import datetime
import logging

from sqlalchemy.orm import Session

from .event import create_google_calendar_event, Event
from .. import get_settings
from ..methods.utils import Group, Lesson
from ..methods.utils import get_lessons_by_group_from_date, get_list_groups

settings = get_settings()
logger = logging.getLogger(__name__)


async def create_google_events_from_db(group_name: str, session: Session) -> list[Event]:
    """
    Creates a timetable for certain group from db.
    Returns list[Event] of events/subjects
    """
    group: Group = (await get_list_groups(session, group_name))[0]
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
                location=lesson.room.name,
                description=f"{lesson.lecturer.first_name} {lesson.lecturer.middle_name} {lesson.lecturer.last_name}",
            )
        )
        if lesson.start_ts.date() == datetime.date.today() + datetime.timedelta(14):
            break
    return list_of_lessons
