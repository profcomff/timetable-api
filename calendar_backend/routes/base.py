import logging

import starlette.requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette import status
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from calendar_backend import exceptions
from calendar_backend import get_settings
from .event import event_router
from .gcal import gcal
from .group import group_router
from .lecturer import lecturer_router
from .room import room_router
from .timetable import timetable_router
from .auth import auth_router

settings = get_settings()
logger = logging.getLogger(__name__)
app = FastAPI(
    description="""API для работы с календарем физфака.
Пример работы на питоне(Создание Room):
```python
import reqests, json
url=f"https://timetable.api.test.profcomff.com"

# Авторизация
beaver = requests.post(f"{url}/token", {"username": "...", "password": "..."})

# Парсинг ответа
auth_data=json.loads(beaver.content)

# Создание
create_room = requests.post(
    f"{url}/timetable/room",
    json={"name": "test", "direction": "South"}, 
    headers={"Authorization": f"Bearer {auth_data.get('access_token')}"}
)

```
"""
)


@app.exception_handler(exceptions.NoGroupFoundError)
async def http_no_group_found_error_handler(request: starlette.requests.Request, exc: exceptions.NoGroupFoundError):
    logger.info(f"No group found error, request: {request.path_params}, error: {exc}")
    return PlainTextResponse("No group found error", status_code=404)


@app.exception_handler(exceptions.NoAudienceFoundError)
async def http_no_room_found_error_handler(request: starlette.requests.Request, exc: exceptions.NoAudienceFoundError):
    logger.info(f"No room found error, request: {request.path_params}, error: {exc}")
    return PlainTextResponse("No room found error", status_code=404)


@app.exception_handler(exceptions.NoTeacherFoundError)
async def http_no_lecturer_found_error_handler(
        request: starlette.requests.Request, exc: exceptions.NoTeacherFoundError
):
    logger.info(f"No lecturer found error, request: {request.path_params}, error: {exc}")
    return PlainTextResponse("No lecturer found error", status_code=404)


@app.exception_handler(exceptions.EventNotFound)
async def http_no_event_found_error_handler(request: starlette.requests.Request, exc: exceptions.EventNotFound):
    logger.info(f"No event found error, request: {request.path_params}, error: {exc}")
    return PlainTextResponse("No event found error", status_code=404)


@app.exception_handler(exceptions.RoomsNotFound)
async def http_no_rooms_found_error_handler(request: starlette.requests.Request, exc: exceptions.RoomsNotFound):
    logger.info(f"No rooms found error, request: {request.path_params}, error: {exc}")
    return PlainTextResponse("No rooms found error", status_code=404)


@app.exception_handler(exceptions.LecturersNotFound)
async def http_no_event_found_error_handler(request: starlette.requests.Request, exc: exceptions.LecturersNotFound):
    logger.info(f"No lecturers found error, request: {request.path_params}, error: {exc}")
    return PlainTextResponse("No lecturers found error", status_code=404)


@app.exception_handler(exceptions.GroupsNotFound)
async def http_no_groups_found_error_handler(request: starlette.requests.Request, exc: exceptions.GroupsNotFound):
    logger.info(f"No groups found error, request: {request.path_params}, error: {exc}")
    return PlainTextResponse("No groups found error", status_code=404)


@app.exception_handler(exceptions.LessonsNotFound)
async def http_no_lessons_found_error_handler(request: starlette.requests.Request, exc: exceptions.LessonsNotFound):
    logger.info(f"No lessons found error, request: {request.path_params}, error: {exc}")
    return PlainTextResponse("No lessons found error", status_code=404)


@app.exception_handler(ValueError)
async def http_value_error_handler(request: starlette.requests.Request, exc: ValueError):
    logger.info(f"Failed to parse data, request: {request.path_params}, exc: {exc}")
    return PlainTextResponse("Error", status_code=500)


@app.exception_handler(Exception)
async def http_critical_error_handler(request: starlette.requests.Request, exc: Exception):
    logger.critical(f"Critical error occurred:{exc}, request: {request.path_params}")
    return PlainTextResponse("Error", status_code=500)


class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_upload_size: int) -> None:
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == 'POST':
            if 'content-length' not in request.headers:
                return Response(status_code=status.HTTP_411_LENGTH_REQUIRED)
            content_length = int(request.headers['content-length'])
            if content_length > self.max_upload_size:
                return Response(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        return await call_next(request)


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
app.add_middleware(LimitUploadSize, max_upload_size=3145728)  # 3MB

app.include_router(gcal)
app.include_router(room_router)
app.include_router(event_router)
app.include_router(lecturer_router)
app.include_router(timetable_router)
app.include_router(group_router)
app.include_router(auth_router)
