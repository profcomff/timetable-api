from .base import Base, Room, Event
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


class RoomEvents(Room):
    events: list[Event] = []


class GetListRoom(Base):
    items: list[Room]
    limit: int
    offset: int
    total: int
