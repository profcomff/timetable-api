from .base import Base, RoomGet, EventGet
from calendar_backend.models import Direction


class RoomPatch(Base):
    name: str | None
    direction: Direction | None
    is_deleted: bool | None

    def __repr__(self):
        return f"Room(name={self.name}, direction={self.direction})"


class RoomPost(Base):
    name: str
    direction: Direction | None


class RoomEvents(RoomGet):
    events: list[EventGet]


class GetListRoom(Base):
    items: list[RoomGet]
    limit: int
    offset: int
    total: int
