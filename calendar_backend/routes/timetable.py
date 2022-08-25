import datetime
import logging
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import list_calendar
from calendar_backend.methods import utils
from .models import base

timetable_router = APIRouter(prefix="/timetable", tags=["Timetable"])
settings = get_settings()
logger = logging.getLogger(__name__)


@timetable_router.get("/by_group/{group_num}", response_model=list[base.Event], deprecated=True)
async def get_timetable_by_group(
    group_num: str, start: datetime.date, end: datetime.date, format: Literal['ics', 'json'] = 'json'
) -> list[base.Event] | FileResponse:
    match format:
        case 'ics':
            logger.debug(f"Downloading .ics file for {group_num} calendar...")
            return await list_calendar.create_ics(group_num, start, end, db.session)
        case 'json':
            logger.debug(f"Getting lessons for group {group_num}")
            group, _ = await utils.get_list_groups(db.session, group_num)
            return [Event.from_orm(row) for row in await utils.get_group_lessons_in_daterange(group=group, date_start=start, date_end=end)]
