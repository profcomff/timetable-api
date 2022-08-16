import logging

from fastapi import APIRouter
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import utils
from calendar_backend.routes.models import Group

group_router = APIRouter(prefix="/timetable/group", tags=["Group"])
settings = get_settings()
logger = logging.getLogger(__name__)


@group_router.get("/{id}", response_model=Group)
async def http_get_group_by_id(id: int) -> Group:
    logger.debug(f"Getting group id:{id}")
    return Group.from_orm(await utils.get_group_by_id(id, db.session))


@group_router.get("/", response_model=list[Group])
async def http_get_groups(filter_group_number: str | None = None) -> list[Group]:
    logger.debug(f"Getting groups list, filter:{filter_group_number}")
    result = await utils.get_list_groups(db.session, filter_group_number)
    if isinstance(result, list):
        return [Group.from_orm(row) for row in result]
    return [Group.from_orm(result)]


@group_router.post("/", response_model=Group)
async def http_create_room(number: str, name: str) -> Group:
    logger.debug(f"Creating group:{number}, {name})")
    Group.number_validate(number)
    return Group.from_orm(await utils.create_group(number, name, db.session))


@group_router.post("/{id}", response_model=Group)
async def http_patch_group(id: int, new_number: str | None = None, new_name: str | None = None) -> Group:
    logger.debug(f"Pathcing group id:{id}")
    group = await utils.get_group_by_id(id, db.session)
    return Group.from_orm(await utils.update_group(group, db.session, new_number, new_name))


@group_router.delete("/{id}", response_model=None)
async def http_delete_group(id: int) -> None:
    logger.debug(f"Deleting group id:{id}")
    group = await utils.get_group_by_id(id, db.session)
    return await utils.delete_group(group, db.session)
