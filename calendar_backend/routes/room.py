import logging

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import utils
from calendar_backend.routes.models import Room, RoomPostPatch

room_router = APIRouter(prefix="/timetable/room", tags=["Room"])
settings = get_settings()
logger = logging.getLogger(__name__)


@room_router.get("/{id}", response_model=Room)
async def http_get_room_by_id(id: int) -> Room:
    logger.debug(f"Getting room id:{id}")
    return Room.from_orm(await utils.get_room_by_id(id, db.session))


@room_router.get("/", response_model=list[Room])
async def http_get_rooms(filter_room_number: str | None = None) -> list[Room]:
    logger.debug(f"Getting rooms list, filter:{filter_room_number}")
    result = await utils.get_list_rooms(db.session, filter_room_number)
    if isinstance(result, list):
        return [Room.from_orm(row) for row in result]
    return [Room.from_orm(result)]


@room_router.post("/", response_model=Room)
async def http_create_room(room: RoomPostPatch) -> Room:
    logger.debug(f"Creating room:{room.name}, {room.direction}")
    if not room.name:
        raise HTTPException(status_code=400, detail="'Name' fields must be not None")
    return Room.from_orm(await utils.create_room(room.name, room.direction, db.session))


@room_router.patch("/{id}", response_model=Room)
async def http_patch_room(id: int, room_pydantic: RoomPostPatch) -> Room:
    logger.debug(f"Pathcing room id:{id}")
    room = await utils.get_room_by_id(id, db.session)
    return Room.from_orm(await utils.update_room(room, db.session, room_pydantic.name, room_pydantic.direction))


@room_router.delete("/{id}", response_model=None)
async def http_delete_room(id: int) -> None:
    logger.debug(f"Deleting room id:{id}")
    room = await utils.get_room_by_id(id, db.session)
    return await utils.delete_room(room, db.session)
