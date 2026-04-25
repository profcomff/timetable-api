from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, Query
from fastapi_sqlalchemy import db

from calendar_backend.models import Event, EventUser
from calendar_backend.routes.models.visit import VisitResponse


router = APIRouter(prefix="/event", tags=["Event: Visit"])


@router.post("/{event_id}/visit", response_model=VisitResponse)
async def set_event_visit_status(
    event_id: int,
    auth: dict = Depends(UnionAuth()),
    visit: str = Query(enum=["no_status", "going", "not_going", "attended"], default="no_status"),
) -> VisitResponse:
    """
    Отметить посещение мероприятия для текущего пользователя.
    """
    user_id = auth.get('id')

    Event.get(event_id, with_deleted=False, session=db.session)

    existing = (
        EventUser.get_all(session=db.session)
        .filter(EventUser.event_id == event_id, EventUser.user_id == user_id)
        .first()
    )

    if existing:
        result = EventUser.update(existing.id, session=db.session, status=visit)
    else:
        result = EventUser.create(
            session=db.session,
            event_id=event_id,
            user_id=user_id,
            status=visit,
        )

    db.session.commit()
    return VisitResponse.model_validate(result)
