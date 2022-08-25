import datetime
import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import utils, auth
from calendar_backend.routes.models import event_models, base

event_router = APIRouter(prefix="/timetable/event", tags=["Event"])
settings = get_settings()
logger = logging.getLogger(__name__)


@event_router.get("/{id}", response_model=event_models.Event)
async def http_get_event_by_id(id: int) -> base.Event:
    logger.debug(f"Getting event id:{id}")
    return base.Event.from_orm(await utils.get_lesson_by_id(id, db.session))


@event_router.get("/")
async def http_get_events(
    start: datetime.date | None = Query(default=None, description="Default: Today"),
    end: datetime.date | None = Query(default=None, description="Default: Tomorrow"),
    group_id: int | None = None,
    lecturer_id: int | None = None,
    room_id: int | None = None,
    detail: list[Literal["comment", "description", ""]] = Query(...),
):
    start = start or datetime.date.today()
    end = end or datetime.date.today() + datetime.timedelta(days=1)
    if not group_id and not lecturer_id and not room_id:
        raise HTTPException(status_code=400, detail=f"One argument reqiured, but no one received")
    if group_id:
        logger.debug(f"Getting events for group_id:{group_id}")
        if lecturer_id or room_id:
            raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
        list_events = await utils.get_group_lessons_in_daterange(
            await utils.get_group_by_id(group_id, db.session), start, end
        )
    if lecturer_id:
        logger.debug(f"Getting events for lecturer_id:{lecturer_id}")
        if group_id or room_id:
            raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
        list_events = await utils.get_lecturer_lessons_in_daterange(
            await utils.get_lecturer_by_id(lecturer_id, db.session), start, end
        )
    if room_id:
        logger.debug(f"Getting events for room_id:{room_id}")
        if lecturer_id or group_id:
            raise HTTPException(status_code=400, detail=f"Only one argument reqiured, but more received")
        list_events = await utils.get_room_lessons_in_daterange(
            await utils.get_room_by_id(room_id, db.session), start, end
        )
    if "" in detail:
        return event_models.GetListEventWithoutLecturerDescriptionAndComments(items=list_events)
    if "comment" not in detail and "description" in detail:
        return event_models.GetListEventWithoutLecturerComments(items=list_events)
    if "description" not in detail and "comment" in detail:
        return event_models.GetListEventWithoutLecturerDescription(items=list_events)
    return event_models.GetListEvent(items=list_events)


@event_router.post("/", response_model=event_models.EventWithoutLecturerDescriptionAndComments)
async def http_create_event(
    lesson: event_models.EventPost, current_user: auth.User = Depends(auth.get_current_user)
) -> event_models.EventWithoutLecturerDescriptionAndComments:
    logger.debug(f"Creating event: {lesson}", extra={"user": current_user})
    return event_models.EventWithoutLecturerDescriptionAndComments.from_orm(
        await utils.create_lesson(
            lesson.room_id, lesson.lecturer_id, lesson.group_id, lesson.name, lesson.start_ts, lesson.end_ts, db.session
        )
    )


@event_router.patch("/{id}", response_model=event_models.EventWithoutLecturerDescriptionAndComments)
async def http_patch_event(
    id: int, lesson_pydantic: event_models.EventPatch, current_user: auth.User = Depends(auth.get_current_user)
) -> event_models.EventWithoutLecturerDescriptionAndComments:
    logger.debug(f"Patcing event id:{id}", extra={"user": current_user})
    lesson = await utils.get_lesson_by_id(id, db.session)
    return event_models.EventWithoutLecturerDescriptionAndComments.from_orm(
        await utils.update_lesson(
            lesson,
            db.session,
            lesson_pydantic.name,
            lesson_pydantic.room_id,
            lesson.group_id,
            [row.id for row in lesson.lecturer],
            lesson.start_ts,
            lesson_pydantic.end_ts,
        )
    )


@event_router.delete("/{id}", response_model=None)
async def http_delete_event(id: int, current_user: auth.User = Depends(auth.get_current_user)) -> None:
    logger.debug(f"Deleting event id:{id}", extra={"user": current_user})
    lesson = await utils.get_lesson_by_id(id, db.session)
    return await utils.delete_lesson(lesson, db.session)


@event_router.post("/{id}/comment", response_model=base.CommentEvent)
async def http_comment_event(id: int, author_name: str, text: str) -> base.CommentEvent:
    logger.debug(f"Creating comment to event: {id}")
    return base.CommentEvent.from_orm(await utils.create_comment_event(id, db.session, text, author_name))


@event_router.patch("/{id}/comment", response_model=base.CommentEvent)
async def http_udpate_comment(comment_id: int, new_text: str) -> base.CommentEvent:
    logger.debug(f"Updating comment: {comment_id}")
    return base.CommentEvent.from_orm(await utils.update_comment_event(comment_id, db.session, new_text))
