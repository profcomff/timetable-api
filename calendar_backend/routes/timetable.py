import asyncio
import datetime
import logging

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import db

import calendar_backend.methods.list_calendar
from calendar_backend import exceptions
from calendar_backend import get_settings
from calendar_backend.methods import utils
from .models import Lesson

timetable_router = APIRouter(prefix="/timetable", tags=["Timetable"])
settings = get_settings()
logger = logging.getLogger(__name__)


@timetable_router.get("/{group}{start}{end}", response_model=list[Lesson])
async def get_timetable(
    group_num: str, start: datetime.date | None, end: datetime.date | None, format: str | None = None
) -> list[Lesson] | FileResponse:
    if format == "ics":
        logger.debug(f"Downloading .ics file for {group_num} calendar...")
        if (
            calendar_backend.methods.list_calendar.check_file_for_creation_date(f"{settings.ICS_PATH}/{group_num}")
            is False
        ):
            logger.debug(f"Calendar for group '{group_num}' found in cache")
            return FileResponse(f"{settings.ICS_PATH}/{group_num}")
        else:
            async with asyncio.Lock():
                logger.debug("Getting user calendar...")
                user_calendar = await calendar_backend.methods.list_calendar.get_user_calendar(
                    group_num, session=db.session, start_date=start, end_date=end
                )
                if not user_calendar:
                    logger.info(f"Failed to create .ics file for group {group_num} (500)")
                    raise HTTPException(status_code=500, detail="Failed to create .ics file")
                logger.debug("Creating .ics file OK")
                return FileResponse(
                    await calendar_backend.methods.list_calendar.create_user_calendar_file(user_calendar, group_num)
                )
    if not format:
        logger.debug(f"Getting lessons for {group_num}")
        group = await utils.get_list_groups(db.session, filter_group_number=group_num)
        return [Lesson.from_orm(row) for row in await utils.get_lessons_by_group(group=group)]
