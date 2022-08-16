import datetime
import logging
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import list_calendar
from calendar_backend.methods import utils
from .models import Lesson

timetable_router = APIRouter(prefix="/timetable", tags=["Timetable"])
settings = get_settings()
logger = logging.getLogger(__name__)


@timetable_router.get("/{group_num}", response_model=list[Lesson])
async def get_timetable(
    group_num: str, start: datetime.date, end: datetime.date, format: Literal['ics', 'json'] = 'json'
) -> list[Lesson] | FileResponse:
    match format:
        case 'ics':
            logger.debug(f"Downloading .ics file for {group_num} calendar...")
            return await list_calendar.create_ics(group_num, start, end)
        case 'json':
            logger.debug(f"Getting lessons for {group_num}")
            group = await utils.get_list_groups(db.session, filter_group_number=group_num)
            return [Lesson.from_orm(row) for row in await utils.get_group_lessons_in_daterange(group=group, date_start=start, date_end=end)]
