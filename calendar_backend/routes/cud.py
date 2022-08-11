import datetime
import logging

from fastapi import APIRouter, HTTPException
from calendar_backend import exceptions
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.routes.models import Room, Group, Lecturer, Lesson
from calendar_backend.methods import utils

cud_router = APIRouter(prefix="/auth-nedeed/timetable/", tags=["CUD"])
settings = get_settings()
logger = logging.getLogger(__name__)


@cud_router.post("/create/room/", response_model=Room)
async def http_create_room(room_pydantic: Room) -> Room:
    try:
        return Room.from_orm(
            await utils.create_room(name=room_pydantic.name, direrction=room_pydantic.direction, session=db.session)
        )
    except ValueError as e:
        logger.info(
            f"Creating room name:{room_pydantic.name}, direction:{room_pydantic.direction} failed with error: {e}"
        )
        raise HTTPException(status_code=500, detail=e)


@cud_router.post("/create/group/", response_model=Group)
async def http_create_group(group_pydantic: Group) -> Group:
    try:
        return Group.from_orm(
            await utils.create_group(number=group_pydantic.number, name=group_pydantic.name, session=db.session)
        )
    except ValueError as e:
        logger.info(f"Creating group name:{group_pydantic.name}, number:{group_pydantic.number} failed with error: {e}")
        raise HTTPException(status_code=500, detail=e)


@cud_router.post("/create/lecturer/", response_model=Lecturer)
async def http_create_lecturer(lecturer_pydantic: Lecturer) -> Lecturer:
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
        logger.info(
            f"Creating lecturer first name:{lecturer_pydantic.first_name},"
            f" middle name:{lecturer_pydantic.middle_name},"
            f" last name:{lecturer_pydantic.last_name} failed with error: {e}"
        )
        raise HTTPException(status_code=500, detail=e)


@cud_router.post("/create/lesson/", response_model=Lesson)
async def http_create_lesson(lesson_pydantic: Lesson) -> Lesson:
    try:
        return Lesson.from_orm(
            await utils.create_lesson(
                name=lesson_pydantic.name,
                room=lesson_pydantic.room,
                lecturer=lesson_pydantic.lecturer,
                group=lesson_pydantic.group,
                start_ts=lesson_pydantic.start_ts,
                end_ts=lesson_pydantic.end_ts,
                session=db.session,
            )
        )
    except ValueError as e:
        logger.info(f"Creating lesson name:{lesson_pydantic.name},"
                    f"room:{lesson_pydantic.room},"
                    f"lecturer: {lesson_pydantic.lecturer},"
                    f"group: {lesson_pydantic.group},"
                    f" start_ts:{lesson_pydantic.start_ts},"
                    f" end_ts:{lesson_pydantic.end_ts}failed with error: {e}")
        raise HTTPException(status_code=500, detail=e)


@cud_router.patch("/patch/room/", response_model=Room)
async def http_patch_room(room_pydantic: Room, new_name: str | None = None) -> Room:
    try:
        room = await utils.get_room_by_name(room_pydantic.name, session=db.session)
        return Room.from_orm(await utils.update_room(room, session=db.session, new_name=new_name))
    except exceptions.NoAudienceFoundError:
        raise HTTPException(status_code=404, detail="No room found")
    except ValueError as e:
        logger.info(f"Failed to patch room: {room_pydantic.name}, {room_pydantic.direction} with error: {e}")
        raise HTTPException(status_code=500, detail=e)


@cud_router.patch("/patch/group/", response_model=Group)
async def http_patch_group(group_pydantic: Group, new_number: str | None = None, new_name: str | None = None) -> Group:
    try:
        group = await utils.get_group_by_name(group_pydantic.name, session=db.session)
        return Group.from_orm(await utils.update_group(group, session=db.session, new_name=new_name, new_number=new_number))
    except exceptions.NoGroupFoundError:
        raise HTTPException(status_code=404, detail="No group found")
    except ValueError as e:
        logger.info(f"Failed to patch room")
        raise HTTPException(status_code=500, detail=e)


@cud_router.patch("/patch/lecturer", response_model=Lecturer)
async def http_patch_lecturer(
    lecturer_pydantic: Lecturer,
    new_first_name: str | None = None,
    new_middle_name: str | None = None,
    new_last_name: str | None = None,
) -> Lecturer:
    pass


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
    pass


@cud_router.delete("/delete/room/")
async def http_delete_room(room_pydantic: Room) -> None:
    pass


@cud_router.delete("/delete/lecturer/")
async def http_delete_lecturer(lecturer_pydantic: Lecturer) -> None:
    pass


@cud_router.delete("/delete/group/")
async def http_delete_group(group_pydantic: Group) -> None:
    pass


@cud_router.delete("/delete/lesson/")
async def http_delete_lesson(lesson_pydantic: Lesson) -> None:
    pass
