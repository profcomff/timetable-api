from pydantic import BaseSettings, Json, PostgresDsn, AnyHttpUrl
from typing import List, Optional
from functools import lru_cache
import json
from os import path


class Settings(BaseSettings):
    """Application settings"""

    DB_DSN: PostgresDsn
    GOOGLE_CREDS: Json
    PATH_TO_GOOGLE_CREDS: str
    APP_URL: Optional[AnyHttpUrl] = None
    REDIRECT_URL: AnyHttpUrl = "https://www.profcomff.com"
    GROUPS: List[str] = []
    TIMETABLE_NAME: str
    ICS_PATH: str
    TAMPLATES_PATH: str
    SCOPES: List[str] = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.email']

    class Config:
        """Pydantic BaseSettings config"""

        case_sensitive = True
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    with open("groups.json", "r") as gf:
        settings.GROUPS = json.load(gf)
    return settings
