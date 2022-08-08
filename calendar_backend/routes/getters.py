import asyncio

from fastapi import APIRouter
from fastapi import Query, HTTPException
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import db

import calendar_backend.methods.list_calendar
from calendar_backend.methods import getters
from calendar_backend.settings import get_settings
from .models import Timetable
from calendar_backend import (
    NotFound,
    NoAudienceFoundError,
    NoTeacherFoundError,
    NoGroupFoundError,
)
from .converters import timetable_converter

getters_router = APIRouter(prefix="/timetable", tags=["Timetable"])
settings = get_settings()


@getters_router.get("/group/{group_num}", response_model=list[Timetable])
async def http_get_timetable_by_group(
    group_num: str = Query(..., description="Group number")
) -> list[dict[str]]:
    try:
        return [
            timetable_converter(row)
            for row in await getters.get_timetable_by_group(
                group=group_num, session=db.session
            )
        ]
    except NoGroupFoundError:
        raise HTTPException(status_code=404, detail="Timetable not found")


@getters_router.get("teacher/{teacher_name}", response_model=list[Timetable])
async def http_get_timetable_by_teacher(
    teacher_name: str = Query(..., description="Teacher name")
) -> list[dict[str]]:
    try:
        return [
            timetable_converter(row)
            for row in await getters.get_timetable_by_teacher(
                teacher=teacher_name, session=db.session
            )
        ]
    except NoTeacherFoundError:
        raise HTTPException(status_code=404, detail="Timetable not found")


@getters_router.get("/audience/{audience_num}", response_model=list[Timetable])
async def http_get_timetable_by_place(
    audience_num: str = Query(..., description="Audience number")
) -> list[dict[str]]:
    try:
        return [
            timetable_converter(row)
            for row in await getters.get_timetable_by_audience(
                audience=audience_num, session=db.session
            )
        ]
    except NoAudienceFoundError:
        raise HTTPException(status_code=404, detail="Timetable not found")


@getters_router.get("/group_weeakday/{group},{weekday}", response_model=list[Timetable])
async def http_get_timetable_by_group_and_weekday(
    group: str = Query(..., description="Group number"),
    weekday: int = Query(..., description="Weekday"),
) -> list[dict[str]]:
    try:
        return [
            timetable_converter(row)
            for row in await getters.get_timetable_by_group_and_weekday(
                group=group, weekday=weekday, session=db.session
            )
        ]
    except NotFound:
        raise HTTPException(status_code=404, detail="Timetable not found")


@getters_router.get("/icsfile/{group}")
async def download_ics_file(group: str = Query(..., description="Group number")):
    if (
        calendar_backend.methods.list_calendar.check_file_for_creation_date(
            f"{settings.ICS_PATH}/{group}"
        )
        is False
    ):
        return FileResponse(f"{settings.ICS_PATH}/{group}")
    else:
        async with asyncio.Lock():
            try:
                user_calendar = (
                    await calendar_backend.methods.list_calendar.get_user_calendar(
                        group, session=db.session
                    )
                )
            except NotFound:
                raise HTTPException(status_code=404, detail="Timetable not found")
            return FileResponse(
                await calendar_backend.methods.list_calendar.create_user_calendar_file(
                    user_calendar, group
                )
            )
