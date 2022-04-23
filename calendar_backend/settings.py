from pydantic import BaseSettings, Json, PostgresDsn, AnyHttpUrl
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""

    DB_DSN: PostgresDsn
    GOOGLE_CREDS: Json
    APP_URL: Optional[AnyHttpUrl] = None
    REDIRECT_URL: AnyHttpUrl = "https://www.profcomff.com"
    GROUPS: List[str] = ["101", "102"]
    TIMETABLE_NAME: str
    ICS_PATH: str

    class Config:
        """Pydantic BaseSettings config"""

        case_sensitive = True
        env_file = "../.env"
