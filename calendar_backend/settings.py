from os import path
from pydantic import BaseSettings, Json, PostgresDsn, AnyHttpUrl
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""

    DB_DSN: PostgresDsn
    GOOGLE_CREDS: Json
    PATH_TO_GOOGLE_CREDS: str = f"{path.dirname(path.dirname(__file__))}/client_secret.json"
    APP_URL: Optional[AnyHttpUrl] = None
    REDIRECT_URL: AnyHttpUrl = "https://www.profcomff.com"
    GROUPS: List[str] = ["101", "102", "202"]
    TIMETABLE_NAME: str = 'timetable'
    DEFAULT_GROUP_STATE: str = '{group: 0}'
    SCOPES: List[str] = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.email']
    ICS_PATH: str

    class Config:
        """Pydantic BaseSettings config"""

        case_sensitive = True
        env_file = ".env"
