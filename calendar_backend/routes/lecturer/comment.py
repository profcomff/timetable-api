from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from calendar_backend.exceptions import ObjectNotFound, ForbiddenAction
from calendar_backend.methods import auth
from calendar_backend.models.db import ApproveStatuses
from calendar_backend.models.db import CommentLecturer as DbCommentLecturer
from calendar_backend.routes.models import (
    CommentLecturer,
    LecturerCommentPost,
    LecturerCommentPatch,
    LecturerComments,
)
from calendar_backend.settings import get_settings

settings = get_settings()

lecturer_comment_router = APIRouter(prefix="/timetable/lecturer/{lecturer_id}", tags=["Lecturer: Comment"])


@lecturer_comment_router.post("/comment/", response_model=CommentLecturer)
async def comment_lecturer(lecturer_id: int, comment: LecturerCommentPost) -> CommentLecturer:
    approve_status = (
        ApproveStatuses.APPROVED if not settings.REQUIRE_REVIEW_LECTURER_COMMENT else ApproveStatuses.PENDING
    )
    return CommentLecturer.from_orm(
        DbCommentLecturer.create(
            lecturer_id=lecturer_id,
            session=db.session,
            **comment.dict(),
            approve_status=approve_status,
        )
    )


@lecturer_comment_router.patch("/comment/{id}", response_model=CommentLecturer)
async def update_comment_lecturer(id: int, lecturer_id: int, comment_inp: LecturerCommentPatch) -> CommentLecturer:
    comment = DbCommentLecturer.get(id=id, only_approved=False, session=db.session)
    if comment.lecturer_id != lecturer_id:
        raise ObjectNotFound(DbCommentLecturer, id)
    if comment.approve_status is not ApproveStatuses.PENDING:
        raise ForbiddenAction(DbCommentLecturer, id)
    return CommentLecturer.from_orm(
        DbCommentLecturer.update(id, session=db.session, **comment_inp.dict(exclude_unset=True))
    )


@lecturer_comment_router.delete("/comment/{id}", response_model=None)
async def delete_comment(id: int, lecturer_id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    comment = DbCommentLecturer.get(id, only_approved=False, session=db.session)
    if comment.lecturer_id != lecturer_id:
        raise ObjectNotFound(DbCommentLecturer, id)
    return DbCommentLecturer.delete(id=id, session=db.session)


@lecturer_comment_router.get("/comment/{id}", response_model=CommentLecturer)
async def get_comment(id: int, lecturer_id: int) -> CommentLecturer:
    comment = DbCommentLecturer.get(id, session=db.session)
    if not comment.lecturer_id == lecturer_id:
        raise ObjectNotFound(DbCommentLecturer, id)
    if comment.approve_status is not None:
        raise ForbiddenAction(DbCommentLecturer, id)
    return CommentLecturer.from_orm(comment)


@lecturer_comment_router.get("/comment/", response_model=LecturerComments)
async def get_all_lecturer_comments(lecturer_id: int, limit: int = 10, offset: int = 0) -> LecturerComments:
    res = DbCommentLecturer.get_all(session=db.session).filter(DbCommentLecturer.lecturer_id == lecturer_id)
    if limit:
        cnt, res = res.count(), res.offset(offset).limit(limit).all()
    else:
        cnt, res = res.count(), res.offset(offset).all()
    return LecturerComments(**{"items": res, "limit": limit, "offset": offset, "total": cnt})