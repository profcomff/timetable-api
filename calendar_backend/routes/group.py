import datetime
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import utils, auth
from calendar_backend.routes.models import GroupEvents, Group, GroupPost, GroupPatch, GetListGroup

group_router = APIRouter(prefix="/timetable/group", tags=["Group"])
settings = get_settings()
logger = logging.getLogger(__name__)


@group_router.get("/{id}", response_model=GroupEvents)
async def http_get_group_by_id(
    id: int, start: datetime.date | None = None, end: datetime.date | None = None
) -> GroupEvents:
    logger.debug(f"Getting group id:{id}")
    group = await utils.get_group_by_id(id, db.session, False)
    result = GroupEvents.from_orm(group)
    if start and end:
        result.events = await utils.get_group_lessons_in_daterange(group, start, end)
    return result


@group_router.get("/", response_model=GetListGroup)
async def http_get_groups(query: str = "", limit: int = 10, offset: int = 0) -> dict[str, Any]:
    logger.debug(f"Getting groups list, filter:{query}")
    result, total = await utils.get_list_groups(db.session, query, limit, offset)
    return {
        "items": [Group.from_orm(row) for row in result],
        "limit": limit,
        "offset": offset,
        "total": total,
    }


@group_router.post("/", response_model=Group)
async def http_create_group(group: GroupPost, current_user: auth.User = Depends(auth.get_current_user)) -> Group:
    logger.debug(f"Creating group: {group}", extra={"user": current_user})
    if await utils.check_group_existing(db.session, group.number):
        raise HTTPException(status_code=423, detail="Already exists")
    return Group.from_orm(await utils.create_group(group.number, group.name, db.session))


@group_router.patch("/{id}", response_model=Group)
async def http_patch_group(
    id: int, group_inp: GroupPatch, current_user: auth.User = Depends(auth.get_current_user)
) -> Group:
    logger.debug(f"Pathcing group id:{id}", extra={"user": current_user})
    group = await utils.get_group_by_id(id, db.session, True)
    return Group.from_orm(
        await utils.update_group(group, db.session, group_inp.number, group_inp.name, group_inp.is_deleted)
    )


@group_router.delete("/{id}", response_model=None)
async def http_delete_group(id: int, current_user: auth.User = Depends(auth.get_current_user)) -> None:
    logger.debug(f"Deleting group id:{id}", extra={"user": current_user})
    group = await utils.get_group_by_id(id, db.session, False)
    return await utils.delete_group(group, db.session)
