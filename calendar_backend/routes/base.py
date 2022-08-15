import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware

from calendar_backend import get_settings
from .room import room_router
from .lecturer import lecturer_router
from .event import event_router
from .timetable import timetable_router
from .gcal import gcal

settings = get_settings()
logger = logging.getLogger(__name__)
app = FastAPI()


@app.exception_handler(Exception)
async def http_critical_error_handler(request, exc):
    logger.critical(f"Critical error occurred:{exc}")
    raise exc


app.add_middleware(
    DBSessionMiddleware,
    db_url=settings.DB_DSN,
    session_args={"autocommit": True},
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.include_router(gcal)
app.include_router(room_router)
app.include_router(event_router)
app.include_router(lecturer_router)
app.include_router(timetable_router)
