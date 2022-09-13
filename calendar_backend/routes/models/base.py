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


class CommentEventGet(Base):
    id: int
    event_id: int
    text: str
    author_name: str
    create_ts: datetime.datetime
    update_ts: datetime.datetime


class GroupGet(Base):
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


class LecturerGet(Base):
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


class RoomGet(Base):
    id: int
    name: str
    direction: str | None

    def __repr__(self):
        return f"Room(id={self.id}, name={self.name}, direction={self.direction})"


class EventGet(Base):
    id: int
    name: str
    room: list[RoomGet]
    group: GroupGet
    lecturer: list[LecturerGet]
    start_ts: datetime.datetime
    end_ts: datetime.datetime
    comments: list[CommentEventGet] | None

    def __repr__(self):
        return (
            f"Lesson(id={self.id}, name={self.name},"
            f" room={self.room}, group={self.group},"
            f" lecturer={self.lecturer}, start_ts={self.start_ts}, end_ts={self.end_ts})"
        )
