import logging

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db

from calendar_backend.models import Room
from calendar_backend.routes.models import GetListRoom, RoomGet, RoomPatch, RoomPost
from calendar_backend.settings import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/room", tags=["Room"])


@router.get("/{id}", response_model=RoomGet)
async def get_room_by_id(id: int) -> RoomGet:
    return RoomGet.from_orm(Room.get(id, session=db.session))


@router.get("/", response_model=GetListRoom)
async def get_rooms(query: str = "", limit: int = 10, offset: int = 0) -> GetListRoom:
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


@router.post("/", response_model=RoomGet)
async def create_room(room: RoomPost, _=Depends(UnionAuth(scopes=["timetable.room.create"]))) -> RoomGet:
    if bool(
        Room.get_all(session=db.session).filter(Room.name == room.name, Room.building == room.building).one_or_none()
    ):
        raise HTTPException(status_code=423, detail="Already exists")
    db_room = Room.create(**room.dict(exclude_unset=True), session=db.session)
    db.session.commit()
    return RoomGet.from_orm(db_room)


@router.patch("/{id}", response_model=RoomGet)
async def patch_room(id: int, room_inp: RoomPatch, _=Depends(UnionAuth(scopes=["timetable.room.update"]))) -> RoomGet:
    room = (
        Room.get_all(session=db.session)
        .filter(Room.name == room_inp.name, Room.building == room_inp.building)
        .one_or_none()
    )
    if room and room.id != id:
        raise HTTPException(status_code=423, detail="Already exists")
    patched = Room.update(id, **room_inp.dict(exclude_unset=True), session=db.session)
    db.session.commit()
    return RoomGet.from_orm(patched)


@router.delete("/{id}", response_model=None)
async def delete_room(id: int, _=Depends(UnionAuth(scopes=["timetable.room.delete"]))) -> None:
    Room.delete(id, session=db.session)
    db.session.commit()
