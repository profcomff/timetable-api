from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from calendar_backend.exceptions import ForbiddenAction, ObjectNotFound
from calendar_backend.models import ApproveStatuses
from calendar_backend.models import CommentEvent as DbCommentEvent
from calendar_backend.routes.models.event import CommentEventGet, EventCommentPatch, EventCommentPost, EventComments
from calendar_backend.settings import get_settings


settings = get_settings()
router = APIRouter(prefix="/event/{event_id}/comment", tags=["Event: Comment"])


@router.post("/", response_model=CommentEventGet)
async def comment_event(event_id: int, comment: EventCommentPost) -> CommentEventGet:
    approve_status = ApproveStatuses.APPROVED if not settings.REQUIRE_REVIEW_EVENT_COMMENT else ApproveStatuses.PENDING
    comment_event = DbCommentEvent.create(
        event_id=event_id, session=db.session, **comment.dict(), approve_status=approve_status
    )
    db.session.commit()
    return CommentEventGet.from_orm(comment_event)


@router.patch("/{id}", response_model=CommentEventGet)
async def update_comment(id: int, event_id: int, comment_inp: EventCommentPatch) -> CommentEventGet:
    comment = DbCommentEvent.get(id, only_approved=False, session=db.session)
    if comment.event_id != event_id:
        raise ObjectNotFound(DbCommentEvent, id)
    if comment.approve_status is not ApproveStatuses.PENDING:
        raise ForbiddenAction(DbCommentEvent, id)
    comment_event = DbCommentEvent.update(id, session=db.session, **comment_inp.dict(exclude_unset=True))
    db.session.commit()
    return CommentEventGet.from_orm(comment_event)


@router.get("/{id}", response_model=CommentEventGet)
async def get_comment(id: int, event_id: int) -> CommentEventGet:
    comment = DbCommentEvent.get(id, session=db.session)
    if not comment.event_id == event_id or comment.approve_status != ApproveStatuses.APPROVED:
        raise ObjectNotFound(DbCommentEvent, id)
    return CommentEventGet.from_orm(comment)


@router.delete("/{id}", response_model=None)
async def delete_comment(
    id: int, event_id: int, _=Depends(UnionAuth(scopes=["timetable.event.comment.delete"]))
) -> None:
    comment = DbCommentEvent.get(id, only_approved=False, session=db.session)
    if comment.event_id != event_id or comment.approve_status != ApproveStatuses.APPROVED:
        raise ObjectNotFound(DbCommentEvent, id)
    DbCommentEvent.delete(id=id, session=db.session)
    db.session.commit()
    return None


@router.get("/", response_model=EventComments)
async def get_event_comments(event_id: int, limit: int = 10, offset: int = 0) -> EventComments:
    res = DbCommentEvent.get_all(session=db.session).filter(DbCommentEvent.event_id == event_id)
    if limit:
        cnt, res = res.count(), res.offset(offset).limit(limit).all()
    else:
        cnt, res = res.count(), res.offset(offset).all()
    return EventComments(**{"items": res, "limit": limit, "offset": offset, "total": cnt})
