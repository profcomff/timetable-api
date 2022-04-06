from fastapi import FastAPI, Query, HTTPException
from connect import timetable, engine

app = FastAPI()


@app.get('/timetable/group/{group_num}')
async def get_timetable_by_group(group: str = Query(..., description="Group number")):
    s = timetable.select().where(timetable.columns.group == group)
    result = engine.execute(s).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return result


@app.get('/timetable/teacher/{teacher_name}')
async def get_timetable_by_teacher(teacher: str = Query(..., description="Teacher name")):
    s = timetable.select().where(timetable.columns.teacher == teacher)
    result = engine.execute(s).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return result


@app.get('/timetable/audience/{audience_num}')
async def get_timetable_by_place(place: str = Query(..., description="Audience number")):
    s = timetable.select().where(timetable.columns.place == place)
    result = engine.execute(s).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return result
