import json

import google.oauth2.credentials
import googleapiclient.discovery
from fastapi_sqlalchemy import db
from googleapiclient.discovery import build
from pydantic import Json
from sqlalchemy.exc import NoResultFound

from calendar_backend.models import Credentials
from calendar_backend.settings import get_settings


settings = get_settings()


def get_calendar_service(id: int) -> googleapiclient.discovery.Resource:
    try:
        user_data = db.query(Credentials).filter_by(id=id).one()
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
            json.loads(user_data.token), settings.SCOPES
        )
        service = build("calendar", "v3", credentials=credentials)
        return service
    except NoResultFound:
        print(f"service for id {id} not found in db")


def get_calendar_service_from_token(token: Json) -> googleapiclient.discovery.Resource:
    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(json.loads(token), settings.SCOPES)
    return build("calendar", "v3", credentials=credentials)
