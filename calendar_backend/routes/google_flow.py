from functools import lru_cache
from fastapi import APIRouter
from fastapi import HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic.types import Json
from urllib.parse import unquote
from googleapiclient.discovery import build
from fastapi_sqlalchemy import db
from google_auth_oauthlib.flow import Flow
from ..google_engine.api_utils import create_calendar_with_timetable
from fastapi_sqlalchemy.exceptions import (
    SessionNotInitialisedError,
    MissingSessionError,
)
from ..models.db import Credentials
from ..settings import get_settings
from ..google_engine.service import get_calendar_service_from_token
from fastapi.templating import Jinja2Templates
import os


google_flow_router = APIRouter(tags=["Auth"])
settings = get_settings()
templates = Jinja2Templates(directory=settings.TAMPLATES_PATH)
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'


@lru_cache
def get_flow(state=""):
    return Flow.from_client_secrets_file(
        client_secrets_file=settings.PATH_TO_GOOGLE_CREDS,
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
    state: Json,
):
    scope = scope.split(unquote("%20"))
    group = str(state.get("group"))
    get_flow().fetch_token(code=code)
    creds = get_flow().credentials
    token: Json = creds.to_json()
    # build service to get an email address
    if group not in settings.GROUPS:
        raise HTTPException(403, "No group provided")
    service = build("oauth2", "v2", credentials=creds)
    email = service.userinfo().get().execute()["email"]

    background_tasks.add_task(create_calendar_with_timetable, get_calendar_service_from_token(token), group)
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

    except SessionNotInitialisedError:
        print("DB session not initialized")
    except MissingSessionError:
        print("Missing db session")

    return templates.TemplateResponse(
        "calendar created.html",
        {
            "request": request,
        },
    )
