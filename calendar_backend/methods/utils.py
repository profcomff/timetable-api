import datetime
from typing import overload

from sqlalchemy import and_
from sqlalchemy.orm import Session

from calendar_backend import exceptions
from calendar_backend.models import Group, Lesson, Lecturer, Room


# Future
# TODO: Tests


async def get_group_by_name(group_num: str, session: Session) -> Group:
    result = session.query(Group).filter(Group.number == group_num).one_or_none()
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
        raise exceptions.NoTeacherFoundError(teacher=f"{first_name} {middle_name} {last_name}")
    return result


async def get_lessons_by_group(group: Group) -> list[Lesson]:
    return group.lessons


async def get_lessons_by_group_from_date(group: Group, date: datetime.date) -> list[Lesson]:
    lessons = group.lessons
    lessons_from_date: list[Lesson] = []
    for lesson in lessons:
        if lesson.start_ts.date() >= date:
            lessons_from_date.append(lesson)
    return lessons_from_date


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
    new_start_ts: datetime.datetime | None = None,
    new_end_ts: datetime.datetime | None = None,
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


async def create_room(name: str, direrction: str, session: Session) -> Room:
    room = Room(name=name, direction=direrction)
    session.add(room)
    session.flush()
    return room


async def create_group(number: str, name: str, session: Session) -> Group:
    group = Group(number=number, name=name)
    session.add(group)
    session.flush()
    return group


async def create_lecturer(first_name: str, middle_name: str, last_name: str, session: Session) -> Lecturer:
    lecturer = Lecturer(first_name=first_name, middle_name=middle_name, last_name=last_name)
    session.add(lecturer)
    session.flush()
    return lecturer


async def create_lesson(
    room: Room,
    lecturer: Lecturer,
    group: Group,
    name: str,
    start_ts: datetime.datetime,
    end_ts: datetime.datetime,
    session: Session,
) -> Lesson:
    lesson = Lesson(
        name=name, room_id=room.id, lecturer_id=lecturer.id, group_id=group.id, start_ts=start_ts, end_ts=end_ts
    )
    session.add(lesson)
    session.flush()
    return lesson


async def get_lesson(
    name: str,
    room: Room,
    group: Group,
    lecturer: Lecturer,
    start_ts: datetime.datetime,
    end_ts: datetime.datetime,
    session: Session,
) -> Lesson:
    result = (
        session.query(Lesson)
        .filter(
            and_(
                Lesson.name == name,
                Lesson.group_id == group.id,
                Lesson.room_id == room.id,
                Lesson.lecturer_id == lecturer.id,
                Lesson.start_ts == start_ts,
                Lesson.end_ts == end_ts,
            )
        )
        .one_or_none()
    )
    if not result:
        raise exceptions.TimetableNotFound()
    return result


async def get_group_lessons_in_daterange(
    group: Group, date_start: datetime.date, date_end: datetime.date
) -> list[Lesson]:
    lessons_list = []
    lessons = group.lessons
    for lesson in lessons:
        if lesson.start_ts.date() >= date_start and lesson.end_ts.date() < date_end:
            lessons_list.append(lesson)
    return lessons_list


async def get_room_lessons_in_daterange(room: Room, date_start: datetime.date, date_end: datetime.date) -> list[Lesson]:
    lessons_list = []
    lessons = room.lessons
    for lesson in lessons:
        if lesson.start_ts.date() >= date_start and lesson.end_ts.date() < date_end:
            lessons_list.append(lesson)
    return lessons_list


async def get_lecturer_lessons_in_daterange(
    lecturer: Lecturer, date_start: datetime.date, date_end: datetime.date
) -> list[Lesson]:
    lessons_list = []
    lessons = lecturer.lessons
    for lesson in lessons:
        if lesson.start_ts.date() >= date_start and lesson.end_ts.date() < date_end:
            lessons_list.append(lesson)
    return lessons_list
