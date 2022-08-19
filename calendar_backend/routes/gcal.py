from functools import lru_cache
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic.types import Json
from urllib.parse import unquote
from googleapiclient.discovery import build, UnknownApiNameOrVersion
from fastapi_sqlalchemy import db
from google_auth_oauthlib.flow import Flow
from ..google_engine import create_calendar_with_timetable
from fastapi_sqlalchemy.exceptions import (
    SessionNotInitialisedError,
    MissingSessionError,
)
from ..models import Credentials
from .. import get_settings
from ..google_engine import get_calendar_service_from_token
from starlette.concurrency import run_in_threadpool
from fastapi.templating import Jinja2Templates
import os
import logging
from calendar_backend.methods import utils


gcal = APIRouter(tags=["Google calendar"])
settings = get_settings()
templates = Jinja2Templates(directory="calendar_backend/templates")
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
logger = logging.getLogger(__name__)


@lru_cache(2)
def get_flow(state=""):
    logger.debug(f"Getting flow with state '{state}'")
    return Flow.from_client_config(
        settings.CLIENT_SECRET,
        scopes=settings.SCOPES,
        state=state,
        redirect_uri=f"{settings.REDIRECT_URL}/credentials",
    )


@gcal.get("/")
async def home(request: Request):
    groups = await utils.create_group_list(db.session)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "groups": groups},
    )


@gcal.get("/flow")
async def get_user_flow(state: str):
    user_flow = get_flow(state)
    return RedirectResponse(user_flow.authorization_url()[0])


@gcal.get("/credentials")
async def get_credentials(
    request: Request,
    background_tasks: BackgroundTasks,
    code: str,
    scope: str,
    state: str,
):
    groups = await utils.create_group_list(db.session)
    scope = scope.split(unquote("%20"))
    group = state
    flow = get_flow()
    try:
        flow.fetch_token(code=code)
        creds = flow.credentials
        token: Json = creds.to_json()
    except ValueError as e:
        logger.info(f"Invalid oauth2 flow session: {e}")
        raise HTTPException(400, "Bad request")
    try:
        # build service to get an email address
        service = build("oauth2", "v2", credentials=creds)
        email = service.userinfo().get().execute()["email"]
        if group not in groups:
            logger.info(f"No group found 404 for user {email}")
            raise HTTPException(404, "No group found")
    except UnknownApiNameOrVersion as e:
        logger.info(f"Invalid Google service: {e}")
    await run_in_threadpool(
        create_calendar_with_timetable,
        get_calendar_service_from_token(token),
        group,
        db.session,
    )
    try:
        db_records = db.session.query(Credentials).filter(Credentials.email == email).all()
        if len(db_records) == 0:
            logger.debug(f"User {email} not found in db. Adding...")
            db.session.add(
                Credentials(
                    group=group,
                    email=email,
                    scope=scope,
                    token=token,
                )
            )
        else:
            logger.debug(f"User {email} is already in db. Updating...")
            db_records.update(
                dict(
                    group=group,
                    scope=scope,
                )
            )
        logger.debug("DB session OK")
    except SessionNotInitialisedError:
        logger.critical("DB session not initialized")
    except MissingSessionError:
        logger.critical("Missing db session")

    return RedirectResponse(settings.REDIRECT_URL)
