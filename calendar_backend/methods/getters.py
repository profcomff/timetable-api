from sqlalchemy import and_
from sqlalchemy.orm import Session
from calendar_backend.models import Timetable
from calendar_backend import (
    NotFound,
    NoAudienceFoundError,
    NoTeacherFoundError,
    NoGroupFoundError,
)


async def get_timetable_by_group(group: str, session: Session) -> list[Timetable]:
    result = session.query(Timetable).filter(Timetable.group == group).all()
    if not result:
        raise NoGroupFoundError(group=group)
    return result


async def get_timetable_by_teacher(teacher: str, session: Session) -> list[Timetable]:
    result = session.query(Timetable).filter(Timetable.teacher == teacher).all()
    if not result:
        raise NoTeacherFoundError(teacher=teacher)
    return result


async def get_timetable_by_audience(audience: str, session: Session) -> list[Timetable]:
    result = session.query(Timetable).filter(Timetable.place == audience).all()
    if not result:
        raise NoAudienceFoundError(audience=audience)
    return result


async def get_timetable_by_group_and_weekday(
    group: str, weekday: int, session: Session
) -> list[Timetable]:
    result = (
        session.query(Timetable)
        .filter(and_(Timetable.group == group, Timetable.weekday == weekday))
        .all()
    )
    if not result:
        raise NotFound()
    return result
