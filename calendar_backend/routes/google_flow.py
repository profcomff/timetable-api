from functools import lru_cache
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic.types import Json
from urllib.parse import unquote
from googleapiclient.discovery import build
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
from fastapi.templating import Jinja2Templates
import os
import logging


google_flow_router = APIRouter(tags=["Auth"])
settings = get_settings()
templates = Jinja2Templates(directory="calendar_backend/templates")
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
logger = logging.getLogger(__name__)


@lru_cache(2)
def get_flow(state=""):
    logger.debug(f"Getting flow with state '{state}'")
    return Flow.from_client_secrets_file(
        client_secrets_file=str(settings.PATH_TO_GOOGLE_CREDS),
        scopes=settings.SCOPES,
        state=state,
        redirect_uri=f"{settings.REDIRECT_URL}/credentials",
    )


@google_flow_router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "groups": settings.GROUPS,
        },
    )


@google_flow_router.get("/flow")
def get_user_flow(state: str):
    user_flow = get_flow(state)
    return RedirectResponse(user_flow.authorization_url()[0])


@google_flow_router.get("/credentials")
def get_credentials(
    request: Request,
    background_tasks: BackgroundTasks,
    code: str,
    scope: str,
    state: str,
):
    scope = scope.split(unquote("%20"))
    group = state
    flow = get_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    token: Json = creds.to_json()
    # build service to get an email address
    service = build("oauth2", "v2", credentials=creds)
    email = service.userinfo().get().execute()["email"]
    if group not in settings.GROUPS:
        logger.info(f"No group found 404 for user {email}")
        raise HTTPException(404, "No group found")

    background_tasks.add_task(
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

    return templates.TemplateResponse(
        "calendar_created.html",
        {
            "request": request,
        },
    )