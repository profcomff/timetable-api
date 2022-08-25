import datetime
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import utils, auth
from calendar_backend.routes.models import group_models, base

group_router = APIRouter(prefix="/timetable/group", tags=["Group"])
settings = get_settings()
logger = logging.getLogger(__name__)


@group_router.get("/{id}", response_model=group_models.GroupEvents)
async def http_get_group_by_id(
    id: int, start: datetime.date | None = None, end: datetime.date | None = None
) -> group_models.GroupEvents:
    logger.debug(f"Getting group id:{id}")
    group = await utils.get_group_by_id(id, db.session)
    result = group_models.GroupEvents.from_orm(group)
    if start and end:
        result.events = await utils.get_group_lessons_in_daterange(group, start, end)
    return result


@group_router.get("/", response_model=group_models.GetListGroup)
async def http_get_groups(query: str = "", limit: int = 10, offset: int = 0) -> dict[str, Any]:
    logger.debug(f"Getting groups list, filter:{query}")
    result, total = await utils.get_list_groups(db.session, query, limit, offset)
    return {
        "items": [group_models.Group.from_orm(row) for row in result],
        "limit": limit,
        "offset": offset,
        "total": total,
    }


@group_router.post("/", response_model=base.Group)
async def http_create_group(
    group: group_models.GroupPost, current_user: auth.User = Depends(auth.get_current_user)
) -> base.Group:
    logger.debug(f"Creating group: {group}", extra={"user": current_user})
    if await utils.check_group_existing(db.session, group.number):
        raise HTTPException(status_code=423, detail="Already exists")
    return base.Group.from_orm(await utils.create_group(group.number, group.name, db.session))


@group_router.patch("/{id}", response_model=base.Group)
async def http_patch_group(
    id: int, group_pydantic: group_models.GroupPatch, current_user: auth.User = Depends(auth.get_current_user)
) -> base.Group:
    logger.debug(f"Pathcing group id:{id}", extra={"user": current_user})
    group = await utils.get_group_by_id(id, db.session)
    return base.Group.from_orm(await utils.update_group(group, db.session, group_pydantic.number, group_pydantic.name))


@group_router.delete("/{id}", response_model=None)
async def http_delete_group(id: int, current_user: auth.User = Depends(auth.get_current_user)) -> None:
    logger.debug(f"Deleting group id:{id}", extra={"user": current_user})
    group = await utils.get_group_by_id(id, db.session)
    return await utils.delete_group(group, db.session)
