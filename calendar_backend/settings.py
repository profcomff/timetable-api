import os
from functools import lru_cache

from auth_lib.fastapi import UnionAuthSettings
from pydantic import AnyHttpUrl, ConfigDict, DirectoryPath, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(UnionAuthSettings, BaseSettings):
    """Application settings"""

    DB_DSN: PostgresDsn = 'postgresql://postgres@localhost:5432/postgres'
    ROOT_PATH: str = '/' + os.getenv('APP_NAME', '')

    REDIRECT_URL: AnyHttpUrl = "https://www.profcomff.com"
    SCOPES: list[str] = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/userinfo.email",
    ]
    STATIC_PATH: DirectoryPath | None = './static'
    ADMIN_SECRET: dict[str, str] = {"admin": "42"}
    REQUIRE_REVIEW_PHOTOS: bool = True
    REQUIRE_REVIEW_LECTURER_COMMENT: bool = True
    REQUIRE_REVIEW_EVENT_COMMENT: bool = True
    CORS_ALLOW_ORIGINS: list[str] = ['*']
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ['*']
    CORS_ALLOW_HEADERS: list[str] = ['*']
    SUPPORTED_FILE_EXTENSIONS: list[str] = ["png", "svg", "jpg", "jpeg", "webp"]

    model_config = ConfigDict(case_sensitive=True, env_file='.env', extra='ignore')


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
