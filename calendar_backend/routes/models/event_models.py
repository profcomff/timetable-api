import datetime

from .base import Base, Room, Group, CommentEvent
from .lecturer_models import LecturerWithoutComments, LecturerWithoutDescription, LecturerWithoutDescriptionAndComments, \
    LecturerWithNonNoneCommentsAndDescription


class EventPatch(Base):
    name: str | None
    room_id: list[int] | None
    group_id: int | None
    lecturer_id: list[int] | None
    start_ts: datetime.datetime | None
    end_ts: datetime.datetime | None
    comments: list[str] | None

    def __repr__(self):
        return (
            f"Lesson(name={self.name},"
            f" room={self.room_id}, group={self.group_id},"
            f" lecturer={self.lecturer_id}, start_ts={self.start_ts}, end_ts={self.end_ts})"
        )


class EventPost(Base):
    name: str
    room_id: list[int]
    group_id: int
    lecturer_id: list[int]
    start_ts: datetime.datetime
    end_ts: datetime.datetime

    def __repr__(self):
        return (
            f"Lesson(name={self.name},"
            f" room={self.room_id}, group={self.group_id},"
            f" lecturer={self.lecturer_id}, start_ts={self.start_ts}, end_ts={self.end_ts})"
        )

class EventWithLecturerCommentsAndDecription(Base):
    id: int
    name: str
    room: list[Room]
    group: Group
    lecturer: list[LecturerWithNonNoneCommentsAndDescription]
    start_ts: datetime.datetime
    end_ts: datetime.datetime


class GetListEvent(Base):
    items: list[EventWithLecturerCommentsAndDecription]


class EventWithoutLecturerComments(Base):
    id: int
    name: str
    room: list[Room]
    group: Group
    lecturer: list[LecturerWithoutComments]
    start_ts: datetime.datetime
    end_ts: datetime.datetime


class EventWithoutLecturerDescription(Base):
    id: int
    name: str
    room: list[Room]
    group: Group
    lecturer: list[LecturerWithoutDescription]
    start_ts: datetime.datetime
    end_ts: datetime.datetime
    comments: list[CommentEvent]


class EventWithoutLecturerDescriptionAndComments(Base):
    id: int
    name: str
    room: list[Room]
    group: Group
    lecturer: list[LecturerWithoutDescriptionAndComments]
    start_ts: datetime.datetime
    end_ts: datetime.datetime


class GetListEventWithoutLecturerComments(Base):
    items: list[EventWithoutLecturerComments]


class GetListEventWithoutLecturerDescription(Base):
    items: list[EventWithoutLecturerDescription]


class GetListEventWithoutLecturerDescriptionAndComments(Base):
    items: list[EventWithoutLecturerDescriptionAndComments]
