import logging

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db

from calendar_backend.methods import auth
from calendar_backend.models import Room
from calendar_backend.routes.models import GetListRoom, RoomPost, RoomPatch, RoomGet
from calendar_backend.settings import get_settings

room_router = APIRouter(prefix="/timetable/room", tags=["Room"])
settings = get_settings()
logger = logging.getLogger(__name__)


@room_router.get("/{id}", response_model=RoomGet)
async def http_get_room_by_id(
    id: int) -> RoomGet:
    return RoomGet.from_orm(Room.get(id, session=db.session))


@room_router.get("/", response_model=GetListRoom)
async def http_get_rooms(query: str = "", limit: int = 10, offset: int = 0) -> GetListRoom:
    res = Room.get_all(session=db.session).filter(Room.name.contains(query))
    if limit:
        cnt, res = res.count(), res.offset(offset).limit(limit).all()
    else:
        cnt, res = res.count(), res.offset(offset).all()
    return GetListRoom(
        **{
            "items": res,
            "limit": limit,
            "offset": offset,
            "total": cnt,
        }
    )


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
    return RoomGet.from_orm(Room.update(id, **room.dict(exclude_unset=True), session=db.session))


@room_router.delete("/{id}", response_model=None)
async def http_delete_room(id: int, current_user: auth.User = Depends(auth.get_current_user)) -> None:
    Room.delete(id, session=db.session)
