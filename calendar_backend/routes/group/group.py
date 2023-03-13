import logging

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db

from calendar_backend.models import Group
from calendar_backend.routes.models import GetListGroup, GroupGet, GroupPatch, GroupPost
from calendar_backend.settings import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)
# DEPRICATED TODO: Drop 2023-04-01
group_router = APIRouter(prefix="/timetable/group", tags=["Group"], deprecated=True)
router = APIRouter(prefix="/group", tags=["Group"])


@group_router.get("/{id}", response_model=GroupGet)  # DEPRICATED TODO: Drop 2023-04-01
@router.get("/{id}", response_model=GroupGet)
async def get_group_by_id(id: int) -> GroupGet:
    return GroupGet.from_orm(Group.get(id, session=db.session))


@group_router.get("/", response_model=GetListGroup)  # DEPRICATED TODO: Drop 2023-04-01
@router.get("/", response_model=GetListGroup)
async def get_groups(query: str = "", limit: int = 10, offset: int = 0) -> GetListGroup:
    res = Group.get_all(session=db.session).filter(Group.number.contains(query))
    if limit:
        cnt, res = res.count(), res.offset(offset).limit(limit).all()
    else:
        cnt, res = res.count(), res.offset(offset).all()
    return GetListGroup(
        **{
            "items": res,
            "limit": limit,
            "offset": offset,
            "total": cnt,
        }
    )


@group_router.post("/", response_model=GroupGet)  # DEPRICATED TODO: Drop 2023-04-01
@router.post("/", response_model=GroupGet)
async def create_group(group: GroupPost, _=Depends(UnionAuth(scopes=["timetable.group.create"]))) -> GroupGet:
    if db.session.query(Group).filter(Group.number == group.number).one_or_none():
        raise HTTPException(status_code=423, detail="Already exists")
    group = Group.create(**group.dict(), session=db.session)
    db.session.commit()
    return GroupGet.from_orm(group)


@group_router.patch("/{id}", response_model=GroupGet)  # DEPRICATED TODO: Drop 2023-04-01
@router.patch("/{id}", response_model=GroupGet)
async def patch_group(
    id: int,
    group_inp: GroupPatch,
    _=Depends(UnionAuth(scopes=["timetable.group.update"])),
) -> GroupGet:
    if (
        bool(query := Group.get_all(session=db.session).filter(Group.number == group_inp.number).one_or_none())
        and query.id != id
    ):
        raise HTTPException(status_code=423, detail="Already exists")
    patched = Group.update(id, **group_inp.dict(exclude_unset=True), session=db.session)
    db.session.commit()
    return GroupGet.from_orm(patched)


@group_router.delete("/{id}", response_model=None)  # DEPRICATED TODO: Drop 2023-04-01
@router.delete("/{id}", response_model=None)
async def delete_group(id: int, _=Depends(UnionAuth(scopes=["timetable.group.delete"]))) -> None:
    Group.delete(id, session=db.session)
    db.session.commit()
