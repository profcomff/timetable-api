from .base import Base, RoomGet, EventGet
from calendar_backend.models import Direction


class RoomPatch(Base):
    name: str | None
    building: str | None
    direction: Direction | None

    def __repr__(self):
        return f"Room(name={self.name}, direction={self.direction})"


class RoomPost(Base):
    name: str
    building: str | None
    direction: Direction | None


class RoomEvents(RoomGet):
    events: list[EventGet]


class GetListRoom(Base):
    items: list[RoomGet]
    limit: int
    offset: int
    total: int
