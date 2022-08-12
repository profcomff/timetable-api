import asyncio
import datetime
import logging

from fastapi import APIRouter
from fastapi import Query, HTTPException
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import db

import calendar_backend.methods.list_calendar
from calendar_backend import exceptions
from calendar_backend import get_settings
from calendar_backend.methods import utils
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


@getters_router.get("/group/{group_number}", response_model=Group)
async def http_get_group(group_number: str) -> Group:
    logger.debug(f"Getting group number:{group_number}")
    try:
        Group.number_validate(group_number)
    except ValueError as e:
        logger.info(f"Value error(pydantic) {group_number}, error: {e} occurred")
        raise HTTPException(status_code=400, detail=e)
    try:
        return Group.from_orm(await utils.get_group_by_name(group_number, session=db.session))
    except exceptions.NoGroupFoundError as e:
        logger.info(f"Failed to get group:{group_number} with error {e}")
        raise HTTPException(status_code=404, detail="No group found")
    except ValueError as e:
        logger.info(f"Failed to get group {group_number}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.get("/lecturer/", response_model=Lecturer)
async def http_get_lecturer(first_name: str, middle_name: str, last_name: str) -> Lecturer:
    logger.debug(f"Getting lecturer {first_name} {middle_name} {last_name}")
    try:
        return Lecturer.from_orm(
            await utils.get_lecturer_by_name(
                first_name=first_name, middle_name=middle_name, last_name=last_name, session=db.session
            )
        )
    except exceptions.NoTeacherFoundError as e:
        logger.info(f"Failed to get lecturer {first_name} {middle_name} {last_name}, error {e} occurred")
        raise HTTPException(status_code=404, detail="Lecturer not found")
    except ValueError as e:
        logger.info(f"Failed to get lecturer {first_name} {middle_name} {last_name}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.get("/room/{room_name}", response_model=Room)
async def http_get_room(room_name: str) -> Room:
    logger.debug(f"Getting room {room_name}")
    try:
        Room.name_validate(room_name)
    except ValueError as e:
        logger.info(f"Failed to get room {room_name}, error {e} occurred")
        raise HTTPException(status_code=400, detail=e)
    try:
        return Room.from_orm(await utils.get_room_by_name(room_name, session=db.session))
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"Failed to get room {room_name}, error {e} occurred")
        raise HTTPException(status_code=404, detail="Room not found")
    except ValueError as e:
        logger.info(f"Failed to get room {room_name}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.post("/group/lessons", response_model=list[Lesson])
async def http_get_group_lessons(group_pydantic: Group) -> list[Lesson]:
    logger.debug(f"Getting lessons for {group_pydantic}")
    try:
        group = await utils.get_group_by_name(group_pydantic.number, session=db.session)
        return [Lesson.from_orm(row) for row in await utils.get_lessons_by_group(group=group)]
    except exceptions.NoGroupFoundError as e:
        logger.info(f"Failed to get lessons for {group_pydantic}, error {e} occurred")
        raise HTTPException(status_code=404, detail="No group found")
    except ValueError as e:
        logger.info(f"Failed to get lessons for {group_pydantic}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.post("/room/lessons", response_model=list[Lesson])
async def http_get_room_lessons(room_pydantic: Room) -> list[Lesson]:
    logger.debug(f"Getting lessons for {room_pydantic}")
    try:
        room = await utils.get_room_by_name(room_name=room_pydantic.name, session=db.session)
        return [Lesson.from_orm(row) for row in await utils.get_lessons_by_room(room=room)]
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"Failed to get lessons for {room_pydantic}, error {e} occurred")
        raise HTTPException(status_code=404, detail="No room found")
    except ValueError as e:
        logger.info(f"Failed to get lessons for {room_pydantic}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.post("/lecturer/lessons", response_model=list[Lesson])
async def http_get_lecturer_lessons(lecturer_pydantic: Lecturer) -> list[Lesson]:
    logger.debug(f"Getting lessons for {lecturer_pydantic}")
    try:
        lecturer = await utils.get_lecturer_by_name(
            lecturer_pydantic.first_name, lecturer_pydantic.middle_name, lecturer_pydantic.last_name, session=db.session
        )
        return [Lesson.from_orm(row) for row in await utils.get_lessons_by_lecturer(lecturer=lecturer)]
    except exceptions.NoTeacherFoundError as e:
        logger.info(f"Failed to get lessons of {lecturer_pydantic}, error {e} occurred")
        raise HTTPException(status_code=404, detail="No lecturer found")
    except ValueError as e:
        logger.info(f"Failed to get lessons of {lecturer_pydantic}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.post("/room/lessons/by-daterange")
async def http_get_room_lessons_in_daterange(
    room_pydantic: Room, date_start: datetime.date, date_end: datetime.date
) -> list[Lesson]:
    try:
        room = await utils.get_room_by_name(room_pydantic.name, session=db.session)
        return [Lesson.from_orm(row) for row in await utils.get_room_lessons_in_daterange(room, date_start, date_end)]
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"Failed to get lessons for {room_pydantic}, error {e} occurred")
        raise HTTPException(status_code=404, detail="No room found")
    except ValueError as e:
        logger.info(f"Failed to get lessons for {room_pydantic}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.post("/lecturer/lessons/by-daterange")
async def http_get_lecturer_lessons_in_daterange(
    lecturer_pydantic: Lecturer, date_start: datetime.date, date_end: datetime.date
) -> list[Lesson]:
    try:
        lecturer = await utils.get_lecturer_by_name(
            lecturer_pydantic.first_name, lecturer_pydantic.middle_name, lecturer_pydantic.last_name, session=db.session
        )
        return [
            Lesson.from_orm(row)
            for row in await utils.get_lecturer_lessons_in_daterange(lecturer, date_start, date_end)
        ]
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"Failed to get lessons for {lecturer_pydantic}, error {e} occurred")
        raise HTTPException(status_code=404, detail="No room found")
    except ValueError as e:
        logger.info(f"Failed to get lessons for {lecturer_pydantic}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)


@getters_router.post("/group/lessons/by-daterange")
async def http_get_room_lessons_in_daterange(
    group_pydantic: Room, date_start: datetime.date, date_end: datetime.date
) -> list[Lesson]:
    try:
        group = await utils.get_room_by_name(group_pydantic.name, session=db.session)
        return [
            Lesson.from_orm(row) for row in await utils.get_ggroup_lessons_in_daterange(group, date_start, date_end)
        ]
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"Failed to get lessons for {group_pydantic}, error {e} occurred")
        raise HTTPException(status_code=404, detail="No room found")
    except ValueError as e:
        logger.info(f"Failed to get lessons for {group_pydantic}, error {e} occurred")
        raise HTTPException(status_code=500, detail=e)
