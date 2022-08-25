from functools import lru_cache

from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl, DirectoryPath, Json


class Settings(BaseSettings):
    """Application settings"""

    DB_DSN: PostgresDsn
    REDIRECT_URL: AnyHttpUrl = "https://www.profcomff.com"
    SCOPES: list[str] = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/userinfo.email",
    ]
    ICS_PATH: DirectoryPath = "cache"
    PHOTO_LECTURER_PATH: DirectoryPath = 'photo/lecturer'
    ADMIN_SECRET: dict[str, str] = {"admin": "42"}
    GOOGLE_CLIENT_SECRET: Json | None
    CORS_ALLOW_ORIGINS: list[str] = ['*']
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ['*']
    CORS_ALLOW_HEADERS: list[str] = ['*']

    class Config:
        """Pydantic BaseSettings config"""

        case_sensitive = True
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
