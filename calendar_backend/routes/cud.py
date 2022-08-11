import datetime
import logging

from fastapi import APIRouter, HTTPException
from calendar_backend import exceptions
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.routes.models import Room, Group, Lecturer, Lesson
from calendar_backend.methods import utils

cud_router = APIRouter(prefix="/auth-nedeed/timetable", tags=["CUD"])
settings = get_settings()
logger = logging.getLogger(__name__)


@cud_router.post("/create/room/", response_model=Room)
async def http_create_room(room_pydantic: Room) -> Room:
    logger.debug(f"Creating {room_pydantic}")
    try:
        return Room.from_orm(
            await utils.create_room(name=room_pydantic.name, direrction=room_pydantic.direction, session=db.session)
        )
    except ValueError as e:
        logger.info(
            f"Creating {room_pydantic} failed with error: {e}"
        )
        raise HTTPException(status_code=500, detail=e)


@cud_router.post("/create/group/", response_model=Group)
async def http_create_group(group_pydantic: Group) -> Group:
    logger.debug(f"Creating {group_pydantic}")
    try:
        return Group.from_orm(
            await utils.create_group(number=group_pydantic.number, name=group_pydantic.name, session=db.session)
        )
    except ValueError as e:
        logger.info(f"Creating {group_pydantic} failed with error: {e}")
        raise HTTPException(status_code=500, detail=e)


@cud_router.post("/create/lecturer/", response_model=Lecturer)
async def http_create_lecturer(lecturer_pydantic: Lecturer) -> Lecturer:
    logger.debug(f"Creating {lecturer_pydantic}")
    try:
        return Lecturer.from_orm(
            await utils.create_lecturer(
                first_name=lecturer_pydantic.first_name,
                middle_name=lecturer_pydantic.middle_name,
                last_name=lecturer_pydantic.last_name,
                session=db.session,
            )
        )
    except ValueError as e:
        logger.info(f"Creating {lecturer_pydantic} failed with error: {e}")
        raise HTTPException(status_code=500, detail=e)


@cud_router.post("/create/lesson/", response_model=Lesson)
async def http_create_lesson(lesson_pydantic: Lesson) -> Lesson:
    logger.debug(f"Creating {lesson_pydantic}")
    try:
        room = await utils.get_room_by_name(lesson_pydantic.room.name, session=db.session)
        lecturer = await utils.get_lecturer_by_name(
            lesson_pydantic.lecturer.first_name,
            lesson_pydantic.lecturer.middle_name,
            lesson_pydantic.lecturer.last_name,
            session=db.session,
        )
        group = await utils.get_group_by_name(lesson_pydantic.group.number, session=db.session)
        return Lesson.from_orm(
            await utils.create_lesson(
                name=lesson_pydantic.name,
                room=room,
                lecturer=lecturer,
                group=group,
                start_ts=lesson_pydantic.start_ts,
                end_ts=lesson_pydantic.end_ts,
                session=db.session,
            )
        )
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"Creating {lesson_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="No room found")
    except exceptions.NoGroupFoundError as e:
        logger.info(f"Creating {lesson_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="No group found")
    except exceptions.NoTeacherFoundError as e:
        logger.info(f"Creating {lesson_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="No lecturer found")
    except ValueError as e:
        logger.info(f"Creating {lesson_pydantic} failed with error: {e}")
        raise HTTPException(status_code=500, detail=e)


@cud_router.patch("/patch/room/", response_model=Room)
async def http_patch_room(room_pydantic: Room, new_name: str | None = None) -> Room:
    logger.debug(f"Patching {room_pydantic}")
    try:
        room = await utils.get_room_by_name(room_pydantic.name, session=db.session)
        return Room.from_orm(await utils.update_room(room, session=db.session, new_name=new_name))
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"Patching {room_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="No room found")
    except ValueError as e:
        logger.info(f"Patching {room_pydantic} failed with error: {e}")
        raise HTTPException(status_code=500, detail=e)


@cud_router.patch("/patch/group/", response_model=Group)
async def http_patch_group(group_pydantic: Group, new_number: str | None = None, new_name: str | None = None) -> Group:
    logger.debug(f"Patching {group_pydantic}")
    try:
        group = await utils.get_group_by_name(group_pydantic.number, session=db.session)
        return Group.from_orm(
            await utils.update_group(group, session=db.session, new_name=new_name, new_number=new_number)
        )
    except exceptions.NoGroupFoundError as e:
        logger.info(f"Patching {group_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="No group found")
    except ValueError as e:
        logger.info(f"Patching {group_pydantic} failed with error: {e}")
        raise HTTPException(status_code=500, detail=e)


@cud_router.patch("/patch/lecturer", response_model=Lecturer)
async def http_patch_lecturer(
    lecturer_pydantic: Lecturer,
    new_first_name: str | None = None,
    new_middle_name: str | None = None,
    new_last_name: str | None = None,
) -> Lecturer:
    logger.debug(f"Patching {lecturer_pydantic}")
    try:
        lecturer = await utils.get_lecturer_by_name(
            first_name=lecturer_pydantic.first_name,
            middle_name=lecturer_pydantic.middle_name,
            last_name=lecturer_pydantic.last_name,
            session=db.session,
        )
        return Lecturer.from_orm(
            await utils.update_lecturer(
                lecturer,
                session=db.session,
                new_first_name=new_first_name,
                new_middle_name=new_middle_name,
                new_last_name=new_last_name,
            )
        )
    except exceptions.NoTeacherFoundError as e:
        logger.info(f"Patching {lecturer_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="No lecturer found")
    except ValueError as e:
        logger.info(f"Patching {lecturer_pydantic} failed with error: {e}")
        raise HTTPException(status_code=500, detail=e)


@cud_router.patch("/patch/lesson/", response_model=Lesson)
async def http_patch_lesson(
    lesson_pydantic: Lesson,
    new_name: str | None = None,
    new_room: Room | None = None,
    new_group: Group | None = None,
    new_lecturer: Lecturer | None = None,
    new_start_ts: datetime.datetime | None = None,
    new_end_ts: datetime.datetime | None = None,
) -> Lesson:
    logger.debug(f"Patching {lesson_pydantic}")
    try:
        lesson = await utils.get_lesson(
            lesson_pydantic.name,
            lesson_pydantic.room,
            lesson_pydantic.group,
            lesson_pydantic.lecturer,
            lesson_pydantic.start_ts,
            lesson_pydantic.end_ts,
            session=db.session,
        )
        return Lesson.from_orm(
            await utils.update_lesson(
                lesson,
                session=db.session,
                new_name=new_name,
                new_group=new_group,
                new_lecturer=new_lecturer,
                new_start_ts=new_start_ts,
                new_end_ts=new_end_ts,
                new_room=new_room,
            )
        )
    except exceptions.TimetableNotFound as e:
        logger.info(f"Patching {lesson_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="Lesson not found")
    except ValueError as e:
        logger.info(f"Patching {lesson_pydantic} failed with error: {e}")
        raise HTTPException(status_code=500, detail=e)

@cud_router.delete("/delete/room/")
async def http_delete_room(room_pydantic: Room) -> None:
    logger.debug(f"Deleting {room_pydantic}")
    try:
        room = await utils.get_room_by_name(room_pydantic.name, session=db.session)
        return await utils.delete_room(room, session=db.session)
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"Deleting {room_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="No room found")


@cud_router.delete("/delete/lecturer/")
async def http_delete_lecturer(lecturer_pydantic: Lecturer) -> None:
    logger.debug(f"Deleting {lecturer_pydantic}")
    try:
        lecture = await utils.get_lecturer_by_name(
            lecturer_pydantic.first_name, lecturer_pydantic.middle_name, lecturer_pydantic.last_name, session=db.session
        )
        return await utils.delete_lecturer(lecture, session=db.session)
    except exceptions.NoTeacherFoundError as e:
        logger.info(f"Deleting {lecturer_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="No lecturer found")


@cud_router.delete("/delete/group/")
async def http_delete_group(group_pydantic: Group) -> None:
    logger.debug(f"Deleting {group_pydantic}")
    try:
        group = await utils.get_group_by_name(group_pydantic.number, session=db.session)
        return await utils.delete_group(group, session=db.session)
    except exceptions.NoGroupFoundError as e:
        logger.info(f"Deleting {group_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="No group found")


@cud_router.delete("/delete/lesson/")
async def http_delete_lesson(lesson_pydantic: Lesson) -> None:
    logger.debug(f"Deleting {lesson_pydantic}")
    try:
        lesson = await utils.get_lesson(
            lesson_pydantic.name,
            lesson_pydantic.room,
            lesson_pydantic.group,
            lesson_pydantic.lecturer,
            lesson_pydantic.start_ts,
            lesson_pydantic.end_ts,
            session=db.session,
        )
        return await utils.delete_lesson(lesson, session=db.session)
    except exceptions.TimetableNotFound as e:
        logger.info(f"Deleting {lesson_pydantic} failed with error: {e}")
        raise HTTPException(status_code=404, detail="Lesson not found")
