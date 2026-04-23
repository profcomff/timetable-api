from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_sqlalchemy import db

from calendar_backend.exceptions import ObjectNotFound
from calendar_backend.models import Event, EventUser
from calendar_backend.routes.models.visit import VisitRequest, VisitResponse


router = APIRouter(prefix="/event", tags=["Event: Visit"])


@router.post("/{event_id}/visit", response_model=VisitResponse)
async def set_event_visit_status(
    event_id: int, visit: VisitRequest, auth: dict = Depends(UnionAuth(scopes=[]))
) -> VisitResponse:
    """
    Отметить посещение мероприятия для текущего пользователя.
    """
    user_id = auth.get('id')
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in authentication data",
        )

    try:
        _ = Event.get(event_id, with_deleted=False, session=db.session)
    except ObjectNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found",
        )

    existing = (
        db.session.query(EventUser)
        .filter(
            EventUser.event_id == event_id,
            EventUser.user_id == user_id,
            EventUser.is_deleted == False,
        )
        .first()
    )

    if existing:
        existing.status = visit.status
        db.session.flush()
        result = existing
    else:
        result = EventUser.create(
            session=db.session,
            event_id=event_id,
            user_id=user_id,
            status=visit.status,
        )

    db.session.commit()

    return VisitResponse(
        id=result.id,
        event_id=result.event_id,
        user_id=result.user_id,
        status=result.status,
        updated_at=result.updated_at.isoformat(),
    )
