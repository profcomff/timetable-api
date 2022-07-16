import asyncio
import list_calendar
import os
import datetime
import json
from email import message
from urllib.parse import unquote
from connect import timetable, engine
from fastapi import FastAPI, Query, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi_sqlalchemy.exceptions import SessionNotInitialisedError, MissingSessionError
from sqlalchemy import and_
from fastapi.templating import Jinja2Templates
from google_auth_oauthlib.flow import Flow
import google.oauth2.credentials
from pydantic.types import Json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_api_utils import copy_timetable_to_user_calendar_list
from timetable_account import get_timetable_account_service
from db import Credentials
from settings import Settings


settings = Settings()
app = FastAPI(root_path=settings.APP_URL)
templates = Jinja2Templates(directory=f"{os.path.dirname(os.path.dirname(__file__))}/templates")
app.add_middleware(DBSessionMiddleware, db_url=settings.DB_DSN)
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
timetable_service = get_timetable_account_service()
user_flow = None


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


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "groups": settings.GROUPS,
        },
    )


@app.get("/flow")
def get_user_flow(state: str):
    global user_flow
    user_flow = Flow.from_client_secrets_file(
        client_secrets_file=settings.PATH_TO_GOOGLE_CREDS,
        scopes=settings.SCOPES,
        state=state,
        redirect_uri=f'{settings.REDIRECT_URL}/credentials'
    )
    return RedirectResponse(user_flow.authorization_url()[0])


@app.get("/credentials")
def get_credentials(
        request: Request,
        background_tasks: BackgroundTasks,
        code: str,
        scope: str,
        state: Json,
):
    scope = scope.split(unquote("%20"))
    group = state.get("group")
    user_flow.fetch_token(code=code)
    creds = user_flow.credentials
    token: Json = creds.to_json()
    # build service to get an email address
    if str(group) not in settings.GROUPS:
        raise HTTPException(403, "No group provided")
    service = build('oauth2', 'v2', credentials=creds)
    email = service.userinfo().get().execute()['email']
    background_tasks.add_task(copy_timetable_to_user_calendar_list, timetable_service, group, email)
    try:
        db_records = db.session.query(Credentials).filter(Credentials.email == email)

        if not db_records.count():
            db.session.add(
                Credentials(
                    group=group,
                    email=email,
                    scope=scope,
                    token=token,
                )
            )
        else:
            db_records.update(
                dict(
                    group=group,
                    scope=scope,
                )
            )
        db.session.commit()

    except SessionNotInitialisedError:
        print("DB session not initialized")
    except MissingSessionError:
        print("Missing db session")

    return templates.TemplateResponse("calendar created.html",
                                      {
                                          "request": request,
                                      })
