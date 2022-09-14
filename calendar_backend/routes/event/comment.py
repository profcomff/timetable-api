from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from calendar_backend.exceptions import ObjectNotFound, ForbiddenAction
from calendar_backend.methods import auth
from calendar_backend.models import ApproveStatuses
from calendar_backend.models import CommentEvent as DbCommentEvent
from calendar_backend.routes.models.event import (
    CommentEventGet,
    EventCommentPost,
    EventCommentPatch,
    EventComments,
)
from calendar_backend.settings import get_settings

settings = get_settings()


event_comment_router = APIRouter(prefix="/timetable/event/{event_id}", tags=["Event: Comment"])

@event_comment_router.post("/comment/", response_model=CommentEventGet)
async def comment_event(event_id: int, comment: EventCommentPost) -> CommentEventGet:
    approve_status = ApproveStatuses.APPROVED if not settings.REQUIRE_REVIEW_EVENT_COMMENT else ApproveStatuses.PENDING
    return CommentEventGet.from_orm(
        DbCommentEvent.create(event_id=event_id, session=db.session, **comment.dict(), approve_status=approve_status)
    )


@event_comment_router.patch("/comment/{id}", response_model=CommentEventGet)
async def update_comment(id: int, event_id: int, comment_inp: EventCommentPatch) -> CommentEventGet:
    comment = DbCommentEvent.get(id, only_approved=False, session=db.session)
    if comment.event_id != event_id:
        raise ObjectNotFound(DbCommentEvent, id)
    if comment.approve_status is not ApproveStatuses.PENDING:
        raise ForbiddenAction(DbCommentEvent, id)
    return CommentEventGet.from_orm(
        DbCommentEvent.update(id, session=db.session, **comment_inp.dict(exclude_unset=True))
    )


@event_comment_router.get("/comment/{id}", response_model=CommentEventGet)
async def get_comment(id: int, event_id: int) -> CommentEventGet:
    comment = DbCommentEvent.get(id, session=db.session)
    if not comment.event_id == event_id or comment.approve_status != ApproveStatuses.APPROVED:
        raise ObjectNotFound(DbCommentEvent, id)
    return CommentEventGet.from_orm(comment)


@event_comment_router.delete("/comment/{id}", response_model=None)
async def delete_comment(id: int, event_id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    comment = DbCommentEvent.get(id, only_approved=False, session=db.session)
    if comment.event_id != event_id or comment.approve_status != ApproveStatuses.APPROVED:
        raise ObjectNotFound(DbCommentEvent, id)
    return DbCommentEvent.delete(id=id, session=db.session)


@event_comment_router.get("/comment/", response_model=EventComments)
async def get_event_comments(event_id: int, limit: int = 10, offset: int = 0) -> EventComments:
    res = DbCommentEvent.get_all(session=db.session).filter(DbCommentEvent.event_id == event_id)
    if limit:
        cnt, res = res.count(), res.offset(offset).limit(limit).all()
    else:
        cnt, res = res.count(), res.offset(offset).all()
    return EventComments(**{"items": res, "limit": limit, "offset": offset, "total": cnt})