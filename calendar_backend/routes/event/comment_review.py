from typing import Literal

from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as

from calendar_backend.exceptions import ObjectNotFound
from calendar_backend.methods import auth
from calendar_backend.models import ApproveStatuses
from calendar_backend.models import CommentEvent as DbCommentEvent
from calendar_backend.routes.models.event import (
    CommentEventGet,
)
from calendar_backend.settings import get_settings


settings = get_settings()
# DEPRICATED TODO: Drop 2023-04-01
event_comment_review_router = APIRouter(prefix="/timetable/event/{event_id}/comment", tags=["Event: Comment Review"], depricated=True)
router = APIRouter(prefix="/event/{event_id}/comment", tags=["Event: Comment Review"])


@event_comment_review_router.get("/review/", response_model=list[CommentEventGet])  # DEPRICATED TODO: Drop 2023-04-01
@router.get("/review/", response_model=list[CommentEventGet])
async def get_unreviewed_comments(
    event_id: int, _: auth.User = Depends(auth.get_current_user)
) -> list[CommentEventGet]:
    comments = (
        DbCommentEvent.get_all(session=db.session, only_approved=False)
        .filter(DbCommentEvent.event_id == event_id, DbCommentEvent.approve_status == ApproveStatuses.PENDING)
        .all()
    )
    return parse_obj_as(list[CommentEventGet], comments)


@event_comment_review_router.post("/{id}/review/", response_model=CommentEventGet)  # DEPRICATED TODO: Drop 2023-04-01
@router.post("/{id}/review/", response_model=CommentEventGet)
async def review_comment(
    id: int,
    event_id: int,
    action: Literal[ApproveStatuses.APPROVED, ApproveStatuses.DECLINED] = ApproveStatuses.DECLINED,
    _: auth.User = Depends(auth.get_current_user),
) -> CommentEventGet:
    comment = DbCommentEvent.get(id, only_approved=False, session=db.session)
    if comment.event_id != event_id or comment.approve_status is not ApproveStatuses.PENDING:
        raise ObjectNotFound(DbCommentEvent, id)
    DbCommentEvent.update(comment.id, approve_status=action, session=db.session)
    if action == ApproveStatuses.DECLINED:
        DbCommentEvent.delete(comment.id, session=db.session)
    db.session.commit()
    return CommentEventGet.from_orm(comment)
