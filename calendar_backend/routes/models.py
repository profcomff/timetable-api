import datetime

from pydantic import BaseModel, validator

from calendar_backend.models import Direction


class Base(BaseModel):
    class Config:
        orm_mode = True


class CommentEvent(Base):
    id: int
    lesson_id: int
    text: str
    author_name: str
    create_ts: datetime.datetime
    update_ts: datetime.datetime


class CommentLecturer(Base):
    id: int
    lecturer_id: int
    text: str
    author_name: str
    create_ts: datetime.datetime
    update_ts: datetime.datetime


class Room(Base):
    id: int
    name: str
    direction: str | None

    def __repr__(self):
        return f"Room(id={self.id}, name={self.name}, direction={self.direction})"


class Group(Base):
    id: int
    name: str | None
    number: str

    @classmethod
    @validator("number")
    def number_validate(cls, v: str):
        if len(v) not in [3, 4]:
            raise ValueError("Group number must contain 3 or 4 characters")
        if not v[0:3].isdigit():
            raise ValueError("Group number format must be 'XYZ' or 'XYZM'")
        return v

    def __repr__(self):
        return f"Group(id={self.id}, name={self.name}, number={self.number})"


class Lecturer(Base):
    id: int
    first_name: str
    middle_name: str
    last_name: str
    photo_link: str | None
    description: str | None
    comments: list[CommentLecturer] | None

    def __repr__(self):
        return f"Lecturer(id={self.id}, first_name={self.first_name}, middle_name={self.middle_name}, last_name={self.last_name})"


class Photos(Base):
    id: int
    link: str


class LecturerPhotos(Lecturer):
    links: list[str]


class Event(Base):
    id: int
    name: str
    room: list[Room]
    group: Group
    lecturer: list[Lecturer]
    start_ts: datetime.datetime
    end_ts: datetime.datetime
    comments: list[CommentEvent] | None

    def __repr__(self):
        return (
            f"Lesson(id={self.id}, name={self.name},"
            f" room={self.room}, group={self.group},"
            f" lecturer={self.lecturer}, start_ts={self.start_ts}, end_ts={self.end_ts})"
        )


class RoomPatch(Base):
    name: str | None
    direction: Direction | None

    def __repr__(self):
        return f"Room(name={self.name}, direction={self.direction})"


class GroupPatch(Base):
    name: str | None
    number: str | None

    @classmethod
    @validator("number")
    def number_validate(cls, v: str):
        if v is None:
            return v
        if len(v) not in [3, 4]:
            raise ValueError("Group number must contain 3 or 4 characters")
        if not v[0:3].isdigit():
            raise ValueError("Group number format must be 'XYZ' or 'XYZM'")
        return v

    def __repr__(self):
        return f"Group(name={self.name}, number={self.number})"


class LecturerPatch(Base):
    first_name: str | None
    middle_name: str | None
    last_name: str | None
    description: str | None

    def __repr__(self):
        return f"Lecturer(first_name={self.first_name}, middle_name={self.middle_name}, last_name={self.last_name})"


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


class RoomPost(Base):
    name: str
    direction: Direction | None


class LecturerPost(Base):
    first_name: str
    middle_name: str
    last_name: str
    description: str | None

    def __repr__(self):
        return f"Lecturer(first_name={self.first_name}, middle_name={self.middle_name}, last_name={self.last_name})"


class GroupPost(Base):
    name: str | None
    number: str

    @classmethod
    @validator("number")
    def number_validate(cls, v: str):
        if v is None:
            return v
        if len(v) not in [3, 4]:
            raise ValueError("Group number must contain 3 or 4 characters")
        if not v[0:3].isdigit():
            raise ValueError("Group number format must be 'XYZ' or 'XYZM'")
        return v

    def __repr__(self):
        return f"Group(name={self.name}, number={self.number})"


class EventPost(Base):
    name: str
    room_id: list[int]
    group_id: int
    lecturer_id: list[int]
    start_ts: datetime.datetime
    end_ts: datetime.datetime
    comments: list[str] | None

    def __repr__(self):
        return (
            f"Lesson(name={self.name},"
            f" room={self.room_id}, group={self.group_id},"
            f" lecturer={self.lecturer_id}, start_ts={self.start_ts}, end_ts={self.end_ts})"
        )


class GetListRoom(Base):
    items: list[Room]
    limit: int
    offset: int
    total: int


class GetListLecturer(Base):
    items: list[Lecturer]
    limit: int
    offset: int
    total: int


class GetListGroup(Base):
    items: list[Group]
    limit: int
    offset: int
    total: int


class GetListEvent(Base):
    items: list[Event]


class RoomEvents(Room):
    events: list[Event] = []


class GroupEvents(Group):
    events: list[Event] = []


class LecturerEvents(Lecturer):
    events: list[Event] = []
