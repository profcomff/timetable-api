import datetime

from .base import Base, CommentEventGet, GroupGet, LecturerGet, RoomGet


class EventPatch(Base):
    name: str | None = None
    room_id: list[int] | None = None
    group_id: list[int] | None = None
    lecturer_id: list[int] | None = None
    start_ts: datetime.datetime | None = None
    end_ts: datetime.datetime | None = None

    def __repr__(self):
        return (
            f"Lesson(name={self.name},"
            f" room={self.room_id}, group={self.group_id},"
            f" lecturer={self.lecturer_id}, start_ts={self.start_ts}, end_ts={self.end_ts})"
        )


class EventPatchName(Base):
    old_name: str
    new_name: str


class EventPatchResult(Base):
    old_name: str
    new_name: str
    updated: int

class EventPost(Base):
    name: str
    room_id: list[int]
    group_id: list[int]
    lecturer_id: list[int]
    start_ts: datetime.datetime
    end_ts: datetime.datetime

    def __repr__(self):
        return (
            f"Lesson(name={self.name},"
            f" room={self.room_id}, group={self.group_id},"
            f" lecturer={self.lecturer_id}, start_ts={self.start_ts}, end_ts={self.end_ts})"
        )


class Event(Base):
    id: int
    name: str
    room: list[RoomGet]
    group: list[GroupGet]
    lecturer: list[LecturerGet]
    start_ts: datetime.datetime
    end_ts: datetime.datetime


class GetListEvent(Base):
    items: list[Event]
    limit: int
    offset: int
    total: int


class EventCommentPost(Base):
    text: str
    author_name: str


class EventCommentPatch(Base):
    text: str | None = None
    author_name: str | None = None


class EventComments(Base):
    items: list[CommentEventGet]
    limit: int
    offset: int
    total: int
