import logging

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db

from calendar_backend import exceptions
from calendar_backend import get_settings
from calendar_backend.methods import utils
from calendar_backend.routes.models import Room

room_router = APIRouter(prefix="/timetable/room", tags=["Room"])
settings = get_settings()
logger = logging.getLogger(__name__)


@room_router.get("/{id}", response_model=Room)
async def http_get_room_by_id(id: int) -> Room:
    logger.debug(f"Getting room id:{id}")
    try:
        return Room.from_orm(await utils.get_room_by_id(id, db.session))
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"No room found error, error {e} occurred")
        raise HTTPException(status_code=404, detail="Room not found")
    except ValueError as e:
        logger.info(f"Failed to parse Room id:{id}, error {e} occurred")
        raise HTTPException(status_code=500, detail="Error")


@room_router.get("/", response_model=list[Room])
async def http_get_rooms(filter_group_number: str | None = None) -> list[Room]:
    logger.debug(f"Getting rooms list, filter:{filter_group_number}")
    return [Room.from_orm(row) for row in await utils.get_list_rooms(db.session, filter_group_number)]


@room_router.post("/", response_model=Room)
async def http_create_room(room: Room) -> Room:
    logger.debug(f"Creating room:{room}")
    try:
        return Room.from_orm(await utils.create_room(room.name, room.direction, db.session))
    except ValueError as e:
        logger.info(f"Failed to create room: {room}, error {e} occurred")
        raise HTTPException(status_code=500, detail="Error")


@room_router.post("/{id}", response_model=Room)
async def http_patch_room(id: int, new_name: str | None = None, new_direction: str | None = None) -> Room:
    logger.debug(f"Pathcing room id:{id}")
    try:
        room = await utils.get_room_by_id(id, db.session)
        return Room.from_orm(await utils.update_room(room, db.session, new_name, new_direction))
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"No room found error, error {e} occurred")
        raise HTTPException(status_code=404, detail="Room not found")
    except ValueError as e:
        logger.info(f"Failed to patch Room id:{id}, error {e} occurred")
        raise HTTPException(status_code=500, detail="Error")


@room_router.delete("/{id}", response_model=None)
async def http_delete_room(id: int) -> None:
    logger.debug(f"Deleting room id:{id}")
    try:
        room = await utils.get_room_by_id(id, db.session)
        return await utils.delete_room(room, db.session)
    except exceptions.NoAudienceFoundError as e:
        logger.info(f"No room found error, error {e} occurred")
        raise HTTPException(status_code=404, detail="Room not found")
