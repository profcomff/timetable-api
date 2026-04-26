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
    visit: str = Query(enum=["no_status", "going", "not_going"], default="no_status"),
) -> VisitResponse:
    """
    Отметить статус посещения мероприятия для текущего пользователя.

    Параметры:
    event_id - id события, которому будет присвоен статус,
    visit - доступные пользователю статусы для присвоения событию (по умолчанию no_status), где:
            no_status - событие без пользовательского решения,
            going - событие, на которое пользователь решил сходить,
            not_going - событие, на которое пользователь решил не ходить.

    Ошибки:
    ObjectNotFound - нет события с таким event_id
    """
    user_id = auth.get('id')

    Event.get(event_id, session=db.session)

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

    return VisitResponse.model_validate(result)
