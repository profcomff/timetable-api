import datetime
import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db

from calendar_backend import get_settings
from calendar_backend.methods import utils
from calendar_backend.routes.models import Room, RoomPatch, RoomPost, GetListRoom, RoomEvents

room_router = APIRouter(prefix="/timetable/room", tags=["Room"])
settings = get_settings()
logger = logging.getLogger(__name__)


@room_router.get("/{id}", response_model=RoomEvents)
async def http_get_room_by_id(
    id: int, start: datetime.date | None = None, end: datetime.date | None = None
) -> RoomEvents:
    logger.debug(f"Getting room id:{id}")
    room = await utils.get_room_by_id(id, db.session)
    if start and end:
        return RoomEvents(**Room.from_orm(room).dict(), events = await utils.get_room_lessons_in_daterange(room, start, end))
    return RoomEvents(**Room.from_orm(room).dict())


@room_router.get("/", response_model=GetListRoom)
async def http_get_rooms(query: str = "", limit: int = 10, offset: int = 0) -> dict[str, Any]:
    logger.debug(f"Getting rooms list, filter:{query}")
    result, total = await utils.get_list_rooms(db.session, query, limit, offset)
    return {"items": [Room.from_orm(row) for row in result],
            "limit": limit,
            "offset": offset,
            "total": total}


@room_router.post("/", response_model=Room)
async def http_create_room(room: RoomPost) -> Room:
    logger.debug(f"Creating room:{room.name}, {room.direction}")
    if await utils.check_room_existing(db.session, room.name):
        raise HTTPException(status_code=423, detail="Already exists")
    return Room.from_orm(await utils.create_room(room.name, room.direction, db.session))


@room_router.patch("/{id}", response_model=Room)
async def http_patch_room(id: int, room_pydantic: RoomPatch) -> Room:
    logger.debug(f"Patching room id:{id}")
    room = await utils.get_room_by_id(id, db.session)
    return Room.from_orm(await utils.update_room(room, db.session, room_pydantic.name, room_pydantic.direction))


@room_router.delete("/{id}", response_model=None)
async def http_delete_room(id: int) -> None:
    logger.debug(f"Deleting room id:{id}")
    room = await utils.get_room_by_id(id, db.session)
    return await utils.delete_room(room, db.session)
