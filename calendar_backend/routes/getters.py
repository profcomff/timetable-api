import asyncio
import logging
from fastapi import APIRouter
from fastapi import Query, HTTPException
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import db

import calendar_backend.methods.list_calendar
from calendar_backend import exceptions
from calendar_backend.methods import getters
from calendar_backend.settings import get_settings
from .models import Timetable

getters_router = APIRouter(prefix="/timetable", tags=["Timetable"])
settings = get_settings()
logger = logging.getLogger(__name__)


@getters_router.get("/group/{group_num}", response_model=list[Timetable])
async def http_get_timetable_by_group(group_num: str = Query(..., description="Group number")) -> list[Timetable]:
    try:
        logger.debug(f"Getting timetable for {group_num}...")
        return [
            Timetable.from_orm(row) for row in await getters.get_timetable_by_group(group=group_num, session=db.session)
        ]
    except exceptions.GroupTimetableNotFound:
        logger.info(f"Timetable for group {group_num} not found (404)")
        raise HTTPException(status_code=404, detail="Timetable not found")


@getters_router.get("teacher/{teacher_name}", response_model=list[Timetable])
async def http_get_timetable_by_teacher(teacher_name: str = Query(..., description="Teacher name")) -> list[Timetable]:
    try:
        logger.debug(f"Getting timetable by teacher {teacher_name}...")
        return [
            Timetable.from_orm(row)
            for row in await getters.get_timetable_by_teacher(teacher=teacher_name, session=db.session)
        ]
    except exceptions.TeacherTimetableNotFound:
        logger.info(f"Timetable for teacher {teacher_name} not found (404)")
        raise HTTPException(status_code=404, detail="Timetable not found")


@getters_router.get("/audience/{audience_num}", response_model=list[Timetable])
async def http_get_timetable_by_place(audience_num: str = Query(..., description="Audience number")) -> list[Timetable]:
    try:
        logger.debug(f"Getting timetable by place {audience_num}...")
        return [
            Timetable.from_orm(row)
            for row in await getters.get_timetable_by_audience(audience=audience_num, session=db.session)
        ]
    except exceptions.AudienceTimetableNotFound:
        logger.info(f"Timetable for place {audience_num} not found (404)")
        raise HTTPException(status_code=404, detail="Timetable not found")


@getters_router.get("/group_weeakday/{group},{weekday}", response_model=list[Timetable])
async def http_get_timetable_by_group_and_weekday(
    group: str = Query(..., description="Group number"),
    weekday: int = Query(..., description="Weekday"),
) -> list[Timetable]:
    try:
        logger.debug(f"Getting timetable by group {group} and weekday {weekday}...")
        return [
            Timetable.from_orm(row)
            for row in await getters.get_timetable_by_group_and_weekday(
                group=group, weekday=weekday, session=db.session
            )
        ]
    except exceptions.GroupTimetableNotFound:
        logger.info(f"Timetable for group {group} and weekday {weekday} not found (404)")
        raise HTTPException(status_code=404, detail="Timetable not found")


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
            except exceptions.GroupTimetableNotFound:
                logger.info(f"Timetable for group {group} not found")
                raise HTTPException(status_code=404, detail="Timetable not found")
            if not user_calendar:
                logger.info(f"Failed to create .ics file for group {group} (500)")
                return HTTPException(status_code=500, detail="Failed to create .ics file")
            logger.debug("Creating .ics file OK")
            return FileResponse(
                await calendar_backend.methods.list_calendar.create_user_calendar_file(user_calendar, group)
            )
