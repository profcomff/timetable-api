import logging
from textwrap import dedent

import starlette.requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from calendar_backend import __version__
from calendar_backend.exceptions import ObjectNotFound, ForbiddenAction, NotEnoughCriteria
from calendar_backend.settings import get_settings

# region DEPRICATED
# TODO: Drop 2023-04-01
from .gcal import gcal
from .lecturer import (
    lecturer_router as old_lecturer_router,
    lecturer_comment_router as old_lecturer_comment_router,
    lecturer_comment_review_router as old_lecturer_comment_review_router,
    lecturer_photo_review_router as old_lecturer_photo_review_router,
    lecturer_photo_router as old_lecturer_photo_router,
)
from .group import group_router as old_group_router
from .room import room_router as old_room_router
from .event import (
    event_router as old_event_router,
    event_comment_router as old_event_comment_router,
    event_comment_review_router as old_event_comment_review_router,
)
# endregion

from .auth import auth_router  # TODO: Replace with PKFF Auth

from .lecturer.lecturer import router as lecturer_router
from .lecturer.comment import router as lecturer_comment_router
from .lecturer.comment_review import router as lecturer_comment_review_router
from .lecturer.photo import router as lecturer_photo_router
from .lecturer.photo_review import router as lecturer_photo_review_router
from .group.group import router as group_router
from .room.room import router as room_router
from .event.event import router as event_router
from .event.comment import router as event_comment_router
from .event.comment_review import router as event_comment_review_router


settings = get_settings()
logger = logging.getLogger(__name__)
app = FastAPI(
    title='Сервис мониторинга активности',
    description=dedent("""
        API для работы с календарем физфака.
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
    """),
    version=__version__,

    # Настраиваем интернет документацию
    root_path=settings.ROOT_PATH if __version__ != 'dev' else '/',
    docs_url=None if __version__ != 'dev' else '/docs',
    redoc_url=None,
)


@app.exception_handler(ObjectNotFound)
async def not_found_error(request: starlette.requests.Request, exc: ObjectNotFound):
    return JSONResponse({"error": exc.args[0], "request": request.path_params}, status_code=404)


@app.exception_handler(ForbiddenAction)
async def forbidden_action(request: starlette.requests.Request, exc: ForbiddenAction):
    return JSONResponse({"error": exc.args[0], "request": request.path_params}, status_code=403)


@app.exception_handler(NotEnoughCriteria)
async def not_enough_criteria(request: starlette.requests.Request, exc: NotEnoughCriteria):
    return JSONResponse({"error": exc.args[0], "request": request.path_params}, status_code=422)


@app.exception_handler(ValueError)
async def http_value_error_handler(request: starlette.requests.Request, exc: ValueError):
    logger.info(f"Failed to parse data, request: {request.path_params}, exc: {exc}")
    return JSONResponse({"error": "Error"}, status_code=500)


@app.exception_handler(Exception)
async def http_critical_error_handler(request: starlette.requests.Request, exc: Exception):
    logger.critical(f"Critical error occurred:{exc}, request: {request.path_params}")
    return JSONResponse({"error": "Error"}, status_code=500)


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
    engine_args={"pool_pre_ping": True},
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
app.add_middleware(LimitUploadSize, max_upload_size=3145728)  # 3MB

app.mount('/static', StaticFiles(directory=settings.STATIC_PATH), 'static')

# region DEPRICATED
# TODO: Drop 2023-04-01
app.include_router(gcal)
app.include_router(auth_router)
app.include_router(lecturer_router)
app.include_router(lecturer_comment_router)
app.include_router(lecturer_comment_review_router)
app.include_router(lecturer_photo_router)
app.include_router(lecturer_photo_review_router)
app.include_router(group_router)
app.include_router(room_router)
app.include_router(event_router)
app.include_router(event_comment_router)
app.include_router(event_comment_review_router)
# endregion
