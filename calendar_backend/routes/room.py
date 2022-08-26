import datetime
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db

from calendar_backend.settings import get_settings
from calendar_backend.methods import utils, auth
from calendar_backend.routes.models import RoomEvents, GetListRoom, RoomPost, RoomPatch, Room

room_router = APIRouter(prefix="/timetable/room", tags=["Room"])
settings = get_settings()
logger = logging.getLogger(__name__)


@room_router.get("/{id}", response_model=RoomEvents)
async def http_get_room_by_id(
    id: int, start: datetime.date | None = None, end: datetime.date | None = None
) -> RoomEvents:
    logger.debug(f"Getting room id:{id}")
    room = await utils.get_room_by_id(id, db.session, False)
    result = RoomEvents.from_orm(room)
    if start and end:
        result.events = await utils.get_room_lessons_in_daterange(room, start, end)
    return result


@room_router.get("/", response_model=GetListRoom)
async def http_get_rooms(query: str = "", limit: int = 10, offset: int = 0) -> dict[str, Any]:
    logger.debug(f"Getting rooms list, filter:{query}")
    result, total = await utils.get_list_rooms(db.session, query, limit, offset)
    return {"items": [Room.from_orm(row) for row in result], "limit": limit, "offset": offset, "total": total}


@room_router.post("/", response_model=Room)
async def http_create_room(room: RoomPost, current_user: auth.User = Depends(auth.get_current_user)) -> Room:
    logger.debug(f"Creating room: {room}", extra={"user": current_user})
    if await utils.check_room_existing(db.session, room.name):
        raise HTTPException(status_code=423, detail="Already exists")
    return Room.from_orm(await utils.create_room(room.name, room.direction, db.session))


@room_router.patch("/{id}", response_model=Room)
async def http_patch_room(
    id: int, room_inp: RoomPatch, current_user: auth.User = Depends(auth.get_current_user)
) -> Room:
    logger.debug(f"Patching room id:{id}", extra={"user": current_user})
    room = await utils.get_room_by_id(id, db.session, True)
    return Room.from_orm(
        await utils.update_room(room, db.session, room_inp.name, room_inp.direction, room_inp.is_deleted)
    )


@room_router.delete("/{id}", response_model=None)
async def http_delete_room(id: int, current_user: auth.User = Depends(auth.get_current_user)) -> None:
    logger.debug(f"Deleting room id:{id}", extra={"user": current_user})
    room = await utils.get_room_by_id(id, db.session, False)
    return await utils.delete_room(room, db.session)
