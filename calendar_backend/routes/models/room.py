from calendar_backend.models import Direction

from .base import Base, EventGet, RoomGet


class RoomPatch(Base):
    name: str | None = None
    building: str | None = None
    building_url: str | None = None
    direction: Direction | None = None

    def __repr__(self):
        return f"Room(name={self.name}, direction={self.direction})"


class RoomPost(Base):
    name: str
    building: str | None = None
    building_url: str | None = None
    direction: Direction | None = None


class RoomEvents(RoomGet):
    events: list[EventGet]


class GetListRoom(Base):
    items: list[RoomGet]
    limit: int
    offset: int
    total: int
