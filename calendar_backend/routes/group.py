import datetime
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db

from calendar_backend.settings import get_settings
from calendar_backend.methods import utils, auth
from calendar_backend.routes.models import GroupEvents, GroupGet, GroupPost, GroupPatch, GetListGroup
from calendar_backend.models import Group

group_router = APIRouter(prefix="/timetable/group", tags=["Group"])
settings = get_settings()
logger = logging.getLogger(__name__)


@group_router.get("/{id}", response_model=GroupEvents)
async def http_get_group_by_id(
    id: int, start: datetime.date | None = None, end: datetime.date | None = None
) -> GroupEvents:
    group = Group.get(id, session=db.session)
    result = GroupEvents.from_orm(group)
    if start and end:
        result.events = await utils.get_group_lessons_in_daterange(group, start, end)
    return result


@group_router.get("/", response_model=GetListGroup)
async def http_get_groups(query: str = "", limit: int = 10, offset: int = 0) -> dict[str, Any]:
    result = Group.get_all(session=db.session).filter(Group.number.contains(query))
    return {
        "items": [GroupGet.from_orm(row) for row in result.offset(offset).limit(limit).all()],
        "limit": limit,
        "offset": offset,
        "total": result.count(),
    }


@group_router.post("/", response_model=GroupGet)
async def http_create_group(group: GroupPost, _: auth.User = Depends(auth.get_current_user)) -> GroupGet:
    if await utils.check_group_existing(db.session, group.number):
        raise HTTPException(status_code=423, detail="Already exists")
    return GroupGet.from_orm(Group.create(**group.dict(), session=db.session))


@group_router.patch("/{id}", response_model=GroupGet)
async def http_patch_group(
    id: int,
    group_inp: GroupPatch,
    _: auth.User = Depends(auth.get_current_user),
) -> GroupGet:
    return Group.update(id, **group_inp.dict(exclude_unset=True), session=db.session)


@group_router.delete("/{id}", response_model=None)
async def http_delete_group(id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    Group.delete(id, session=db.session)
