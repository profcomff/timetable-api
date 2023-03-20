"""DEPRICATED TODO: Drop 2023-04-01
"""
import logging
import os
from functools import lru_cache
from urllib.parse import unquote

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db
from fastapi_sqlalchemy.exceptions import MissingSessionError, SessionNotInitialisedError
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import UnknownApiNameOrVersion, build
from pydantic.types import Json

from calendar_backend.google_engine import create_calendar_with_timetable, get_calendar_service_from_token
from calendar_backend.models import Credentials, Group
from calendar_backend.settings import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="calendar_backend/templates")
# DEPRICATED TODO: Drop 2023-04-01
gcal = APIRouter(tags=["Utils: Google"], deprecated=True)


os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"


@lru_cache(2)
def get_flow(state=""):
    return Flow.from_client_config(
        settings.GOOGLE_CLIENT_SECRET,
        scopes=settings.SCOPES,
        state=state,
        redirect_uri=f"{settings.REDIRECT_URL}/credentials",
    )


@gcal.get("/flow")
async def get_user_flow(state: str):
    if settings.GOOGLE_CLIENT_SECRET:
        user_flow = get_flow(state)
        return RedirectResponse(user_flow.authorization_url()[0])
    else:
        logger.info("Missing google service credentials")
        return HTTPException(502, "Connection to google failed")


@gcal.get("/credentials")
async def get_credentials(
    background_tasks: BackgroundTasks,
    code: str,
    scope: str,
    state: str,
):
    groups = [
        f"{row.number}, {row.name}" if row.name else f"{row.number}" for row in db.session.query(Group).filter().all()
    ]
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
        service = build("oauth2", "v2", credentials=creds, cache_discovery=False)
        email = service.userinfo().get().execute()["email"]
        if group not in groups:
            logger.info(f"No group found 404 for user {email}")
            raise HTTPException(404, "No group found")
    except UnknownApiNameOrVersion as e:
        logger.info(f"Invalid Google service: {e}")
    background_tasks.add_task(
        create_calendar_with_timetable,
        get_calendar_service_from_token(token),
        group,
        db.session,
    )
    try:
        db_records = db.session.query(Credentials).filter(Credentials.email == email)
        if len(db_records.all()) == 0:
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
        logger.debug("DB session OK")
    except SessionNotInitialisedError:
        logger.critical("DB session not initialized")
    except MissingSessionError:
        logger.critical("Missing db session")
    return RedirectResponse(settings.REDIRECT_URL)
