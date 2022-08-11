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
from .models import Room, Lecturer, Group

getters_router = APIRouter(prefix="/timetable", tags=["Timetable"])
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
                logger.info(f"Timetable for group {group} not found")
                raise HTTPException(status_code=404, detail="Timetable not found")
            if not user_calendar:
                logger.info(f"Failed to create .ics file for group {group} (500)")
                return HTTPException(status_code=500, detail="Failed to create .ics file")
            logger.debug("Creating .ics file OK")
            return FileResponse(
                await calendar_backend.methods.list_calendar.create_user_calendar_file(user_calendar, group)
            )


@getters_router.get("/group/future/{group_number}", response_model=Group)
async def http_get_group(group_number: str) -> Group:
    try:
        return Group.from_orm(utils.get_group_by_name(group_number, session=db.session))
    except exceptions.NoGroupFoundError:
        raise HTTPException(status_code=404, detail="No group found")
    except ValueError as e:
        logger.info(f"Failed to get group {group_number}, error {e} occurred")


@getters_router.get("/lecturer/future", response_model=Lecturer)
async def http_get_lecturer(lecturer: Lecturer) -> Lecturer:
    try:
        return Lecturer.from_orm(utils.get_lecturer_by_name(**lecturer.dict(), session=db.session))
    except exceptions.TeacherTimetableNotFound:
        raise HTTPException(status_code=404, detail="Lecturer not found")
    except ValueError as e:
        logger.info(f"Failed to get lecturer {lecturer}, error {e} occurred")


@getters_router.get("/room/future", response_model=Room)
async def http_get_room(room_name: str) -> Room:
    try:
        return Room.from_orm(utils.get_room_by_name(room_name, session=db.session))
    except exceptions.AudienceTimetableNotFound:
        raise HTTPException(status_code=404, detail="Room not found")
    except ValueError as e:
        logger.info(f"Failed to get room {room_name}, error {e} occurred")
