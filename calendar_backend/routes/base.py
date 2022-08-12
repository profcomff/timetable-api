import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware

from calendar_backend import get_settings
from .cud import cud_router
from .getters import getters_router
from .google_flow import google_flow_router

settings = get_settings()
logger = logging.getLogger(__name__)
app = FastAPI()


@app.exception_handler(Exception)
async def http_value_error_handler(exc):
    logger.critical(f"Critical error occurred:{exc}")
    raise exc


app.add_middleware(
    DBSessionMiddleware,
    db_url=settings.DB_DSN,
    session_args={"autocommit": True},
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(getters_router)
app.include_router(google_flow_router)
app.include_router(cud_router)
