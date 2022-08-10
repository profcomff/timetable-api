from sqlalchemy import and_
from sqlalchemy.orm import Session
from calendar_backend.models import Timetable
from calendar_backend import exceptions

async def get_timetable_by_group(group: str, session: Session) -> list[Timetable]:
    """
    Returns the group's timetable
    """
    result = session.query(Timetable).filter(Timetable.group == group).all()
    if not result:
        raise exceptions.GroupTimetableNotFound(group=group)
    return result


async def get_timetable_by_teacher(teacher: str, session: Session) -> list[Timetable]:
    """
    Returns the teacher's timetable
    """
    result = session.query(Timetable).filter(Timetable.teacher == teacher).all()
    if not result:
        raise exceptions.TeacherTimetableNotFound(teacher=teacher)
    return result


async def get_timetable_by_audience(audience: str, session: Session) -> list[Timetable]:
    """
    returns classroom timetable
    """
    result = session.query(Timetable).filter(Timetable.place == audience).all()
    if not result:
        raise exceptions.AudienceTimetableNotFound(audience=audience)
    return result


async def get_timetable_by_group_and_weekday(
    group: str, weekday: int, session: Session
) -> list[Timetable]:
    """
    Returns the schedule of the group on this day of the week
    """
    result = (
        session.query(Timetable)
        .filter(and_(Timetable.group == group, Timetable.weekday == weekday))
        .all()
    )
    if not result:
        raise exceptions.GroupTimetableNotFound(group=group)
    return result
