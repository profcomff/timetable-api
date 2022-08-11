import asyncio
import logging

from fastapi import APIRouter
from fastapi import Query, HTTPException
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import db

import calendar_backend.methods.list_calendar
from calendar_backend import exceptions
from calendar_backend.methods import utils
from calendar_backend.settings import get_settings
from .models import Room, Lecturer, Group, Lesson

getters_router = APIRouter(prefix="/timetable/get", tags=["Timetable"])
settings = get_settings()
logger = logging.getLogger(__name__)


@getters_router.get("/icsfile/{group}")
async def download_ics_file(group: str = Query(..., description="Group number")):
    logger.debug(f"Downloading .ics file for {group} calendar...")
    if calendar_backend.methods.list_calendar.check_file_for_creation_date(f"{settings.ICS_PATH}/{group}") is False:
        logger.debug(f"Calendar for group '{group}' found in cache")
        return FileResponse(f"{settings.ICS_PATH}/{group}")
    else:
        async with asyncio.Lock():
            try:
                logger.debug("Getting user calendar...")
                user_calendar = await calendar_backend.methods.list_calendar.get_user_calendar(
                    group, session=db.session
                )
            except exceptions.NoGroupFoundError:
                logger.info(f"Group {group} not found")
                raise HTTPException(status_code=404, detail="Timetable not found")
            if not user_calendar:
                logger.info(f"Failed to create .ics file for group {group} (500)")
                return HTTPException(status_code=500, detail="Failed to create .ics file")
            logger.debug("Creating .ics file OK")
            return FileResponse(
                await calendar_backend.methods.list_calendar.create_user_calendar_file(user_calendar, group)
            )


@getters_router.get("/group//{group_number}", response_model=Group)
async def http_get_group(group_number: str) -> Group:
    try:
        Group.number_validate(group_number)
    except ValueError as e:
        logger.info(f"Value error(pydantic) {group_number}, error: {e}")
        raise HTTPException(status_code=400, detail=e)
    try:
        return Group.from_orm(utils.get_group_by_name(group_number, session=db.session))
    except exceptions.NoGroupFoundError:
        raise HTTPException(status_code=404, detail="No group found")
    except ValueError as e:
        logger.info(f"Failed to get group {group_number}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.get("/lecturer/", response_model=Lecturer)
async def http_get_lecturer(lecturer: Lecturer) -> Lecturer:
    try:
        return Lecturer.from_orm(utils.get_lecturer_by_name(**lecturer.dict(), session=db.session))
    except exceptions.NoTeacherFoundError:
        raise HTTPException(status_code=404, detail="Lecturer not found")
    except ValueError as e:
        logger.info(f"Failed to get lecturer {lecturer}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.get("/room/{room_name}", response_model=Room)
async def http_get_room(room_name: str) -> Room:
    try:
        Room.name_validate(room_name)
    except ValueError as e:
        logger.info(f"Value error(pydantic) {room_name}, error: {e}")
        raise HTTPException(status_code=400, detail=e)
    try:
        return Room.from_orm(utils.get_room_by_name(room_name, session=db.session))
    except exceptions.NoAudienceFoundError:
        raise HTTPException(status_code=404, detail="Room not found")
    except ValueError as e:
        logger.info(f"Failed to get room {room_name}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.get("/group/lessons", response_model=list[Lesson])
async def http_get_group_lessons(group: Group) -> list[Lesson]:
    try:
        return [Lesson.from_orm(row) for row in await utils.get_lessons_by_group(group=group)]
    except exceptions.NoGroupFoundError:
        raise HTTPException(status_code=404, detail="No group found")
    except ValueError as e:
        logger.info(f"Failed to get group lessons {group}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.get("/room/lessons", response_model=list[Lesson])
async def http_get_room_lessons(room: Room) -> list[Lesson]:
    try:
        return [Lesson.from_orm(row) for row in await utils.get_lessons_by_room(room=room)]
    except exceptions.NoAudienceFoundError:
        raise HTTPException(status_code=404, detail="No room found")
    except ValueError as e:
        logger.info(f"Failed to get room lessons {room}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.get("/lecturer/lessons", response_model=list[Lesson])
async def http_get_lecturer_lessons(lecturer: Lecturer) -> list[Lesson]:
    try:
        return [Lesson.from_orm(row) for row in await utils.get_lessons_by_lecturer(lecturer=lecturer)]
    except exceptions.NoTeacherFoundError:
        raise HTTPException(status_code=404, detail="No lecturer found")
    except ValueError as e:
        logger.info(f"Failed to get room lessons {lecturer}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)