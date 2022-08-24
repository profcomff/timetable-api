import datetime
import random
import string

import aiofiles
from fastapi import UploadFile, File
from sqlalchemy.orm import Session

from calendar_backend import exceptions, get_settings
from calendar_backend.models import Group, Lesson, Lecturer, Room, Direction
from calendar_backend.models.db import Photo, CommentsLecturer, CommentsLesson, LessonsLecturers, LessonsRooms

settings = get_settings()


# TODO: Tests


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


async def get_list_groups(
    session: Session, query: str = "", limit: int = 10, offset: int = 0
) -> tuple[list[Group], int]:
    result = session.query(Group).filter(Group.number.contains(query)).offset(offset)
    if limit > 0:
        result = result.limit(limit)
    return result.all(), result.count()


async def get_list_rooms(session: Session, query: str = "", limit: int = 10, offset: int = 0) -> tuple[list[Room], int]:
    result = session.query(Room).filter(Room.name.contains(query)).offset(offset)
    if limit > 0:
        result = result.limit(limit)
    return result.all(), result.count()


async def get_list_lecturers(
    session: Session, query: str = "", limit: int = 10, offset: int = 0
) -> tuple[list[Lecturer], int]:
    result = session.query(Lecturer).filter(Lecturer.search(query)).offset(offset)
    if limit > 0:
        result = result.limit(limit)
    return result.all(), result.count()


async def get_list_lessons(session: Session, filter_name: str | None = None) -> list[Lesson] | Lesson:
    result = (
        session.query(Lesson).filter(Lesson.name == filter_name).all() if filter_name else session.query(Lesson).all()
    )
    if not result:
        raise exceptions.LessonsNotFound()
    return result


async def get_lessons_by_group_from_date(group: Group, date: datetime.date) -> list[Lesson]:
    lessons = group.lessons
    lessons_from_date: list[Lesson] = []
    for lesson in lessons:
        if lesson.start_ts.date() >= date:
            lessons_from_date.append(lesson)
    return lessons_from_date


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
    new_description: str | None = None,
) -> Lecturer:
    lecturer.first_name = new_first_name or lecturer.first_name
    lecturer.middle_name = new_middle_name or lecturer.middle_name
    lecturer.last_name = new_last_name or lecturer.last_name
    lecturer.description = new_description or lecturer.description
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
    lesson.room = [session.query(Room).get(id) for id in new_room_id] if new_room_id is not None else lesson.room
    lesson.lecturer = (
        [session.query(Lecturer).get(id) for id in new_lecturer_id] if new_lecturer_id is not None else lesson.lecturer
    )
    lesson.start_ts = new_start_ts or lesson.start_ts
    lesson.end_ts = new_end_ts or lesson.end_ts
    session.flush()
    return lesson


async def delete_room(room: Room, session: Session) -> None:
    session.query(LessonsRooms).filter(LessonsRooms.room_id == room.id).delete()
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
    session.query(LessonsLecturers).filter(LessonsLecturers.lecturer_id == lecturer.id).delete()
    for row in lecturer.lessons:
        session.delete(row)
    for row in lecturer.photos:
        session.delete(row)
    for row in lecturer.comments:
        session.delete(row)
    session.delete(lecturer)
    session.flush()
    return None


async def delete_lesson(lesson: Lesson, session: Session) -> None:
    for row in lesson.comments:
        session.delete(row)
    session.delete(lesson)
    session.flush()
    return None


async def create_room(name: str, direction: Direction | None, session: Session) -> Room:
    room = Room(name=name, direction=direction)
    session.add(room)
    session.flush()
    return room


async def create_group(number: str, name: str, session: Session) -> Group:
    group = Group(number=number, name=name)
    session.add(group)
    session.flush()
    return group


async def create_lecturer(
    first_name: str, middle_name: str, last_name: str, description: str, session: Session
) -> Lecturer:
    lecturer = Lecturer(first_name=first_name, middle_name=middle_name, last_name=last_name, description=description)
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
    for row in room_id:
        if not session.query(Room).filter(Room.id == row).one_or_none():
            raise exceptions.NoAudienceFoundError(row)
    for row in lecturer_id:
        if not session.query(Lecturer).filter(Lecturer.id == row).one_or_none():
            raise exceptions.NoTeacherFoundError(row)
    room = [await get_room_by_id(row, session) for row in room_id]
    lecturer = [await get_lecturer_by_id(row, session) for row in lecturer_id]
    lesson = Lesson(name=name, room=room, lecturer=lecturer, group_id=group_id, start_ts=start_ts, end_ts=end_ts)
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


async def check_group_existing(session: Session, group_num: str) -> bool:
    if session.query(Group).filter(Group.number == group_num).one_or_none():
        return True
    return False


async def check_room_existing(session: Session, room_name: str) -> bool:
    if session.query(Room).filter(Room.name == room_name).one_or_none():
        return True
    return False


async def check_lecturer_existing(session: Session, first_name: str, middle_name: str, last_name: str) -> bool:
    if (
        session.query(Lecturer)
        .filter(Lecturer.first_name == first_name, Lecturer.middle_name == middle_name, Lecturer.last_name == last_name)
        .one_or_none()
    ):
        return True
    return False


async def upload_lecturer_photo(lecturer_id: int, session: Session, file: UploadFile = File(...)) -> Photo:
    random_string = ''.join(random.choice(string.ascii_letters) for i in range(32))
    path = f"{settings.PHOTO_LECTURER_PATH}/{random_string}.{file.content_type.split('/')[1]}"
    async with aiofiles.open(path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        photo = Photo(lecturer_id=lecturer_id, link=random_string)
        session.add(photo)
        session.flush()
    return photo


async def create_comment_event(event_id: int, session: Session, text: str, author_name: str) -> CommentsLesson:
    comment = CommentsLesson(text=text, author_name=author_name, lesson_id=event_id)
    session.add(comment)
    session.flush()
    return comment


async def create_comment_lecturer(lecturer_id: int, session: Session, text: str, author_name: str) -> CommentsLecturer:
    comment = CommentsLecturer(text=text, author_name=author_name, lecturer_id=lecturer_id)
    session.add(comment)
    session.flush()
    return comment


async def update_comment_lecturer(comment_id: int, session: Session, new_text: str) -> CommentsLecturer:
    comment = session.query(CommentsLecturer).get(comment_id)
    comment.text = new_text
    session.flush()
    return comment


async def update_comment_event(comment_id: int, session: Session, new_text: str) -> CommentsLesson:
    comment = session.query(CommentsLesson).get(comment_id)
    comment.text = new_text
    session.flush()
    return comment


async def get_photo_by_id(photo_id: int, session: Session) -> Photo:
    photo = session.query(Photo).get(photo_id)
    if not photo:
        raise exceptions.PhotoNotFoundError(photo_id)
    return photo


async def set_lecturer_avatar(lecturer_id: int, photo_id: int, session: Session) -> Lecturer:
    lecturer = await get_lecturer_by_id(lecturer_id, session)
    if photo_id in [row.id for row in lecturer.photos]:
        lecturer.avatar = await get_photo_by_id(photo_id, session)
        return lecturer
    else:
        raise exceptions.LecturerPhotoNotFoundError(id=photo_id, lecturer_id=lecturer_id)