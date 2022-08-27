import datetime
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db

from calendar_backend.settings import get_settings
from calendar_backend.methods import utils, auth
from calendar_backend.routes.models import RoomEvents, GetListRoom, RoomPost, RoomPatch, RoomGet
from calendar_backend.models import Room

room_router = APIRouter(prefix="/timetable/room", tags=["Room"])
settings = get_settings()
logger = logging.getLogger(__name__)


@room_router.get("/{id}", response_model=RoomEvents)
async def http_get_room_by_id(
    id: int, start: datetime.date | None = None, end: datetime.date | None = None
) -> RoomEvents:
    room = Room.get(id, session=db.session)
    result = RoomEvents.from_orm(room)
    if start and end:
        result.events = await utils.get_room_lessons_in_daterange(room, start, end)
    return result


@room_router.get("/", response_model=GetListRoom)
async def http_get_rooms(query: str = "", limit: int = 10, offset: int = 0) -> dict[str, Any]:
    result = Room.get_all(session=db.session).filter(Room.name.contains(query)).offset(offset).limit(limit)
    return {
        "items": [RoomGet.from_orm(row) for row in result.all()],
        "limit": limit,
        "offset": offset,
        "total": result.count(),
    }


@room_router.post("/", response_model=RoomGet)
async def http_create_room(room: RoomPost, current_user: auth.User = Depends(auth.get_current_user)) -> RoomGet:
    if bool(Room.get_all(session=db.session).filter(Room.name == room.name).one_or_none()):
        raise HTTPException(status_code=423, detail="Already exists")
    return RoomGet.from_orm(Room.create(name=room.name, direction=room.direction, session=db.session))


@room_router.patch("/{id}", response_model=RoomGet)
async def http_patch_room(
    id: int, room: RoomPatch, current_user: auth.User = Depends(auth.get_current_user)
) -> RoomGet:
    if bool(Room.get_all(session=db.session).filter(Room.name == room.name).one_or_none()):
        raise HTTPException(status_code=423, detail="Already exists")
    return Room.update(id, **room.dict(exclude_unset=True), session=db.session)


@room_router.delete("/{id}", response_model=None)
async def http_delete_room(id: int, current_user: auth.User = Depends(auth.get_current_user)) -> None:
    Room.delete(id, session=db.session)
