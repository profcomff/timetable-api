import datetime

from pydantic import BaseModel

from calendar_backend.models import EventUserStatus


class VisitRequest(BaseModel):
    status: EventUserStatus


class VisitResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    status: EventUserStatus
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
