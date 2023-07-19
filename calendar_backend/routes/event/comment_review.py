from typing import Literal

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from pydantic import TypeAdapter

from calendar_backend.exceptions import ObjectNotFound
from calendar_backend.models import ApproveStatuses
from calendar_backend.models import CommentEvent as DbCommentEvent
from calendar_backend.routes.models.event import CommentEventGet
from calendar_backend.settings import get_settings


settings = get_settings()
router = APIRouter(prefix="/event/{event_id}/comment", tags=["Event: Comment Review"])


@router.get("/review/", response_model=list[CommentEventGet])
async def get_unreviewed_comments(
    event_id: int, _=Depends(UnionAuth(scopes=["timetable.event.comment.review"]))
) -> list[CommentEventGet]:
    comments = (
        DbCommentEvent.get_all(session=db.session, only_approved=False)
        .filter(DbCommentEvent.event_id == event_id, DbCommentEvent.approve_status == ApproveStatuses.PENDING)
        .all()
    )
    adapter = TypeAdapter(list[CommentEventGet])
    return adapter.validate_python(comments)


@router.post("/{id}/review/", response_model=CommentEventGet)
async def review_comment(
    id: int,
    event_id: int,
    action: Literal[ApproveStatuses.APPROVED, ApproveStatuses.DECLINED] = ApproveStatuses.DECLINED,
    _=Depends(UnionAuth(scopes=["timetable.event.comment.review"])),
) -> CommentEventGet:
    comment = DbCommentEvent.get(id, only_approved=False, session=db.session)
    if comment.event_id != event_id or comment.approve_status is not ApproveStatuses.PENDING:
        raise ObjectNotFound(DbCommentEvent, id)
    DbCommentEvent.update(comment.id, approve_status=action, session=db.session)
    if action == ApproveStatuses.DECLINED:
        DbCommentEvent.delete(comment.id, session=db.session)
    db.session.commit()
    return CommentEventGet.model_validate(comment)
