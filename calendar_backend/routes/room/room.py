import logging

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db

from calendar_backend.methods import auth
from calendar_backend.models import Room
from calendar_backend.routes.models import GetListRoom, RoomPost, RoomPatch, RoomGet
from calendar_backend.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
# DEPRICATED TODO: Drop 2023-04-01
room_router = APIRouter(prefix="/timetable/room", tags=["Room"], deprecated=True)
router = APIRouter(prefix="/room", tags=["Room"])


@room_router.get("/{id}", response_model=RoomGet)  # DEPRICATED TODO: Drop 2023-04-01
@router.get("/{id}", response_model=RoomGet)
async def get_room_by_id(id: int) -> RoomGet:
    return RoomGet.from_orm(Room.get(id, session=db.session))


@room_router.get("/", response_model=GetListRoom)  # DEPRICATED TODO: Drop 2023-04-01
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


@room_router.post("/", response_model=RoomGet)  # DEPRICATED TODO: Drop 2023-04-01
@router.post("/", response_model=RoomGet)
async def create_room(room: RoomPost, _: auth.User = Depends(auth.get_current_user)) -> RoomGet:
    if bool(
        Room.get_all(session=db.session).filter(Room.name == room.name, Room.building == room.building).one_or_none()
    ):
        raise HTTPException(status_code=423, detail="Already exists")
    db_room = Room.create(**room.dict(exclude_unset=True), session=db.session)
    db.session.commit()
    return RoomGet.from_orm(db_room)


@room_router.patch("/{id}", response_model=RoomGet)  # DEPRICATED TODO: Drop 2023-04-01
@router.patch("/{id}", response_model=RoomGet)
async def patch_room(id: int, room_inp: RoomPatch, _: auth.User = Depends(auth.get_current_user)) -> RoomGet:
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


@room_router.delete("/{id}", response_model=None)  # DEPRICATED TODO: Drop 2023-04-01
@router.delete("/{id}", response_model=None)
async def delete_room(id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    Room.delete(id, session=db.session)
    db.session.commit()
