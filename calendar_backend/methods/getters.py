import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session
from calendar_backend.models import Timetable, Group, Lesson, Lecturer, Room
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


async def get_timetable_by_group_and_weekday(group: str, weekday: int, session: Session) -> list[Timetable]:
    """
    Returns the schedule of the group on this day of the week
    """
    result = session.query(Timetable).filter(and_(Timetable.group == group, Timetable.weekday == weekday)).all()
    if not result:
        raise exceptions.GroupTimetableNotFound(group=group)
    return result


async def get_group_by_name(group_num: str, session: Session) -> Group:
    result = session.query(Group).filter(Group.name == group_num).one_or_none()
    if not result:
        raise exceptions.NoGroupFoundError(group=group_num)
    return result


async def get_room_by_name(room_name: str, session: Session) -> Room:
    result = session.query(Room).filter(Room.name == room_name).one_or_none()
    if not result:
        raise exceptions.NoAudienceFoundError(audience=room_name)
    return result


async def get_lecturer_by_name(first_name: str, middle_name: str, last_name: str, session: Session) -> Lecturer:
    result = (
        session.query(Lecturer)
        .filter(
            and_(
                Lecturer.first_name == first_name, Lecturer.middle_name == middle_name, Lecturer.last_name == last_name
            )
        )
        .one_or_none()
    )
    if not result:
        raise exceptions.NoTeacherFoundError
    return result


async def get_lessons_by_group(group: Group) -> list[Lesson]:
    return group.lessons


async def get_lessons_by_lecturer(lecturer: Lecturer) -> list[Lesson]:
    return lecturer.lessons


async def get_lessons_by_room(room: Room) -> list[Lesson]:
    return room.lessons


async def update_room(room: Room, session: Session, new_name: str | None = None) -> Room:
    room.name = new_name or room.name
    session.flush()
    return room


async def update_group(
    group: Group, session: Session, new_number: str | None = None, new_name: str | None = None
) -> Group:
    group.number = new_number or group.number
    group.name = new_name or group.name
    session.flush()
    return group


async def update_lecturer(
    lecturer: Lecturer,
    session: Session,
    new_first_name: str | None = None,
    new_middle_name: str | None = None,
    new_last_name: str | None = None,
) -> Lecturer:
    lecturer.first_name = new_first_name or lecturer.first_name
    lecturer.middle_name = new_middle_name or lecturer.middle_name
    lecturer.last_name = new_last_name or lecturer.last_name
    session.flush()
    return lecturer


async def update_lesson(
    lesson: Lesson,
    session: Session,
    new_name: str | None = None,
    new_room: Room | None = None,
    new_group: Group | None = None,
    new_lecturer: Lecturer | None = None,
    new_start_ts: datetime.time | None = None,
    new_end_ts: datetime.time | None = None,
) -> Lesson:
    lesson.name = new_name or lesson.name
    lesson.group = new_group or lesson.group
    lesson.room_id = new_room.id or lesson.room_id
    lesson.lecturer_id = new_lecturer.id or lesson.lecturer_id
    lesson.start_ts = new_start_ts or lesson.start_ts
    lesson.end_ts = new_end_ts or lesson.end_ts
    session.flush()
    return lesson


async def delete_room(room: Room, session: Session) -> None:
    session.delete(room)
    session.flush()
    return None


async def delete_group(group: Group, session: Session) -> None:
    session.delete(group)
    session.flush()
    return None


async def delete_lecturer(lecturer: Lecturer, session: Session) -> None:
    session.delete(lecturer)
    session.flush()
    return None


async def delete_lesson(lesson: Lesson, session: Session) -> None:
    session.delete(lesson)
    session.flush()
    return None


