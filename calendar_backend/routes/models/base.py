import datetime

from pydantic import BaseModel, validator


class Base(BaseModel):
    class Config:
        orm_mode = True


class CommentLecturer(Base):
    id: int
    lecturer_id: int
    text: str
    author_name: str
    create_ts: datetime.datetime
    update_ts: datetime.datetime


class CommentEvent(Base):
    id: int
    lesson_id: int
    text: str
    author_name: str
    create_ts: datetime.datetime
    update_ts: datetime.datetime


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
    avatar_id: int | None
    avatar_link: str | None
    description: str | None
    comments: list[CommentLecturer] | None

    def __repr__(self):
        return f"Lecturer(id={self.id}, first_name={self.first_name}, middle_name={self.middle_name}, last_name={self.last_name})"


class Room(Base):
    id: int
    name: str
    direction: str | None

    def __repr__(self):
        return f"Room(id={self.id}, name={self.name}, direction={self.direction})"


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
