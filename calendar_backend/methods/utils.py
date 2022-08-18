import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from calendar_backend import exceptions
from calendar_backend.models import Group, Lesson, Lecturer, Room

# TODO: Tests
from calendar_backend.settings import Settings


async def get_group_by_id(group_id: int, session: Session) -> Group:
    result = session.query(Group).filter(Group.id == group_id).one_or_none()
    if not result:
        raise exceptions.NoGroupFoundError(group=group_id)
    return result


async def get_room_by_id(room_id: int, session: Session) -> Room:
    result = session.query(Room).filter(Room.id == room_id).one_or_none()
    if not result:
        raise exceptions.NoAudienceFoundError(audience=room_id)
    return result


async def get_lecturer_by_id(lecturer_id: int, session: Session) -> Lecturer:
    result = session.query(Lecturer).filter(Lecturer.id == lecturer_id).one_or_none()
    if not result:
        raise exceptions.NoTeacherFoundError(teacher=lecturer_id)
    return result


async def get_list_groups(session: Session, filter_group_number: str | None = None) -> Group | list[Group]:
    result = (
        session.query(Group).filter(Group.number == filter_group_number).one_or_none()
        if filter_group_number
        else session.query(Group).all()
    )
    if not result:
        raise exceptions.GroupsNotFound()
    return result


async def get_list_rooms(session: Session, filter_room_number: str | None = None) -> list[Room] | Room:
    result = (
        session.query(Room).filter(Room.name == filter_room_number).one_or_none()
        if filter_room_number
        else session.query(Room).all()
    )
    if not result:
        raise exceptions.RoomsNotFound()
    return result


async def get_list_lecturers(
    session: Session,
    filter_first_name: str | None = None,
    filter_middle_name: str | None = None,
    filter_last_name: str | None = None,
) -> list[Lecturer]:
    if filter_last_name and filter_middle_name and filter_last_name:
        result = (
            session.query(Lecturer)
            .filter(
                Lecturer.first_name == filter_first_name,
                Lecturer.middle_name == filter_middle_name,
                Lecturer.last_name == filter_last_name,
            )
            .all()
        )
    else:
        result = session.query(Lecturer).all()
    if not result:
        raise exceptions.LecturersNotFound()
    return result


async def get_list_lessons(session: Session, filter_name: str | None = None) -> list[Lesson] | Lesson:
    result = (
        session.query(Lesson).filter(Lesson.name == filter_name).all() if filter_name else session.query(Lesson).all()
    )
    if not result:
        raise exceptions.LessonsNotFound()
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


async def get_lesson_by_id(id: int, session: Session) -> Lesson:
    result = session.query(Lesson).filter(Lesson.id == id).one_or_none()
    if not result:
        raise exceptions.EventNotFound(id)
    return result


async def update_room(
    room: Room, session: Session, new_name: str | None = None, new_direction: str | None = None
) -> Room:
    room.name = new_name or room.name
    room.direction = new_direction or room.direction
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
    new_room_id: list[int] | None = None,
    new_group_id: int | None = None,
    new_lecturer_id: list[int] | None = None,
    new_start_ts: datetime.datetime | None = None,
    new_end_ts: datetime.datetime | None = None,
) -> Lesson:
    lesson.name = new_name or lesson.name
    lesson.group_id = new_group_id or lesson.group
    lesson.room = [session.query(Room).get(id) for id in new_room_id] if new_room_id is not None else lesson.room_id
    lesson.lecturer = [session.query(Lecturer).get(id) for id in new_lecturer_id] if new_lecturer_id is not None else lesson.lecturer
    lesson.start_ts = new_start_ts or lesson.start_ts
    lesson.end_ts = new_end_ts or lesson.end_ts
    session.flush()
    return lesson


async def delete_room(room: Room, session: Session) -> None:
    for row in room.lessons:
        session.delete(row)
    session.delete(room)
    session.flush()
    return None


async def delete_group(group: Group, session: Session) -> None:
    for row in group.lessons:
        session.delete(row)
    session.delete(group)
    session.flush()
    return None


async def delete_lecturer(lecturer: Lecturer, session: Session) -> None:
    for row in lecturer.lessons:
        session.delete(row)
    session.delete(lecturer)
    session.flush()
    return None


async def delete_lesson(lesson: Lesson, session: Session) -> None:
    session.delete(lesson)
    session.flush()
    return None


async def create_room(name: str, direrction: str | None, session: Session) -> Room:
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
    room_id: list[int],
    lecturer_id: list[int],
    group_id: int,
    name: str,
    start_ts: datetime.datetime,
    end_ts: datetime.datetime,
    session: Session,
) -> Lesson:
    if not session.query(Group).filter(Group.id == group_id).one_or_none():
        raise exceptions.NoGroupFoundError(group_id)
    if not session.query(Room).filter(Room.id == room_id).one_or_none():
        raise exceptions.NoAudienceFoundError(room_id)
    if not session.query(Lecturer).filter(Lecturer.id == lecturer_id).one_or_none():
        raise exceptions.NoTeacherFoundError(lecturer_id)
    room = await get_room_by_id(room_id, session)
    lecturer = await get_lecturer_by_id(lecturer_id, session)
    lesson = Lesson(
        name=name, room=[room], lecturer=[lecturer], group_id=group_id, start_ts=start_ts, end_ts=end_ts
    )
    session.add(lesson)
    session.flush()
    return lesson


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


async def create_group_list(session: Session) -> list:
    groups: list[Group] = session.query(Group).filter().all()
    return [f"{row.number}, {row.name}" if row.name else f"{row.number}" for row in groups]
