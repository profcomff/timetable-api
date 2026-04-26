import datetime

from calendar_backend.models import EventUserStatus

from .base import Base


# class VisitRequest(Base):
#     status: EventUserStatus


class VisitResponse(Base):
    id: int
    event_id: int
    user_id: int
    status: EventUserStatus
    updated_at: datetime.datetime
