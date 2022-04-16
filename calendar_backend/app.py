import asyncio

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import and_
from settings import Settings

import list_calendar
from connect import timetable, engine

app = FastAPI()
settings = Settings()


@app.get('/timetable/group/{group_num}')
async def get_timetable_by_group(group_num: str = Query(..., description="Group number")) -> list[dict[str]]:
    s = timetable.select().where(timetable.columns.group == group_num)
    result = engine.execute(s).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return result


@app.get('/timetable/teacher/{teacher_name}')
async def get_timetable_by_teacher(teacher_name: str = Query(..., description="Teacher name")) -> list[dict[str]]:
    s = timetable.select().where(timetable.columns.teacher == teacher_name)
    result = engine.execute(s).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return result


@app.get('/timetable/audience/{audience_num}')
async def get_timetable_by_place(audience_num: str = Query(..., description="Audience number")) -> list[dict[str]]:
    s = timetable.select().where(timetable.columns.place == audience_num)
    result = engine.execute(s).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return result


@app.get('/timetable/group_weeakday/{group},{weekday}')
async def get_timetable_by_group_and_weekday(group: str = Query(..., description="Group number"),
                                             weekday: int = Query(..., description="Weekday")) -> list[dict[str]]:
    s = timetable.select().where(and_(timetable.columns.group == group, timetable.columns.weekday == weekday))
    result = engine.execute(s).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return result


@app.get('/timetable/icsfile/{group}')
async def download_ics_file(group: str = Query(..., description="Group number")):
    if list_calendar.check_file_for_creation_date(f"{settings.ICS_PATH}{group}") is False:
        return FileResponse(f"{settings.ICS_PATH}{group}")
    else:
        async with asyncio.Lock():
            user_calendar = await list_calendar.get_user_calendar(group)
            return FileResponse(await list_calendar.create_user_calendar_file(user_calendar, group))
