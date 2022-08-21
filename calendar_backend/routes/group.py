import datetime
import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db

from calendar_backend import get_settings, exceptions
from calendar_backend.methods import utils
from calendar_backend.routes.models import Group, GroupPatch, GroupPost, GetListGroup, GroupEvents

group_router = APIRouter(prefix="/timetable/group", tags=["Group"])
settings = get_settings()
logger = logging.getLogger(__name__)


@group_router.get("/{id}", response_model=GroupEvents)
async def http_get_group_by_id(
    id: int, start: datetime.date | None = None, end: datetime.date | None = None
) -> GroupEvents:
    logger.debug(f"Getting group id:{id}")
    group = await utils.get_group_by_id(id, db.session)
    if start and end:
        return GroupEvents(**group.dict(), events=await utils.get_group_lessons_in_daterange(group, start, end))
    return GroupEvents(**group.dict())


@group_router.get("/", response_model=GetListGroup)
async def http_get_groups(filter_group_number: str = "", limit: int = 10, offset: int = 0) -> dict[str, Any]:
    logger.debug(f"Getting groups list, filter:{filter_group_number}")
    result = await utils.get_list_groups(db.session, filter_group_number, limit, offset)
    if not result:
        return {"items": []}
    if isinstance(result, list):
        return {"items": [Group.from_orm(row) for row in result]}
    return {"items": [Group.from_orm(result)]}


@group_router.post("/", response_model=Group)
async def http_create_group(group: GroupPost) -> Group:
    logger.debug(f"Creating group:{group})")
    if await utils.check_group_existing(db.session, group.number):
        raise HTTPException(status_code=423, detail="Already exists")
    return Group.from_orm(await utils.create_group(group.number, group.name, db.session))


@group_router.patch("/{id}", response_model=Group)
async def http_patch_group(id: int, group_pydantic: GroupPatch) -> Group:
    logger.debug(f"Pathcing group id:{id}")
    group = await utils.get_group_by_id(id, db.session)
    return Group.from_orm(await utils.update_group(group, db.session, group_pydantic.number, group_pydantic.name))


@group_router.delete("/{id}", response_model=None)
async def http_delete_group(id: int) -> None:
    logger.debug(f"Deleting group id:{id}")
    group = await utils.get_group_by_id(id, db.session)
    return await utils.delete_group(group, db.session)
