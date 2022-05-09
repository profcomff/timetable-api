import os

from pydantic import BaseSettings, Json, PostgresDsn, AnyHttpUrl
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""

    DB_DSN: PostgresDsn
    GOOGLE_CREDS: Json
    PATH_TO_GOOGLE_CREDS: str = '/Users/new/PycharmProjects/timetable-backend-2/client_secret.json'
    APP_URL: Optional[AnyHttpUrl] = None
    REDIRECT_URL: AnyHttpUrl = "https://www.profcomff.com"
    GROUPS: List[str] = ["101", "102", "202"]
    TIMETABLE_NAME: str = 'timetable'
    DEFAULT_GROUP_STATE = '{group: 0}'
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.email']
    ICS_PATH: str = ''

    class Config:
        """Pydantic BaseSettings config"""

        case_sensitive = True
        env_file = ".env"
