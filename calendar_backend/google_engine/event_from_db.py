import datetime

from sqlalchemy.orm import Session

from .. import get_settings
from ..methods.utils import get_lessons_by_group_from_date, get_group_by_name, get_room_by_name
from ..methods.utils import Group, Lesson
from .event import create_google_calendar_event, Event
import logging

settings = get_settings()
logger = logging.getLogger(__name__)


async def create_google_events_from_db(group_name: str, session: Session) -> list[Event]:
    """
    Creates a timetable for certain group from db timetable.
    Returns list[Event] of events/subjects
    """
    group: Group = await get_group_by_name(group_name, session)
    group_lessons: list[Lesson] = await get_lessons_by_group_from_date(group, datetime.date.today())
    list_of_lessons: list[Event] = []
    logger.debug(f"Getting list of subjects for {group}...")
    for lesson in group_lessons:
        list_of_lessons.append(
            create_google_calendar_event(
                summary=lesson.name,
                start_time=f"{lesson.start_ts}",
                end_time=f"{lesson.end_ts}",
                location=lesson.room.name,
                description=f"{lesson.lecturer.first_name} {lesson.lecturer.middle_name} {lesson.lecturer.last_name}",
            )
        )
    return list_of_lessons
