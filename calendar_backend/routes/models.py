import datetime

from pydantic import BaseModel, validator

from calendar_backend.models import Direction, LectureRooms


class Timetable(BaseModel):
    """
    User-friendly timetable format
    """

    start: datetime.time
    end: datetime.time
    odd: bool
    even: bool
    weekday: int
    group: str
    subject: str
    place: str | None
    teacher: str | None

    class Config:
        orm_mode = True


class Room(BaseModel):
    name: str
    direction: str

    @classmethod
    @validator("direction")
    def direction_validate(cls, v: str):
        if v not in Direction:
            raise ValueError(f"Direction must be either {Direction.NORTH} or {Direction.SOUTH}")
        return v

    @classmethod
    @validator("name")
    def name_validate(cls, v: str):
        if v in LectureRooms:
            return v
        if len(v) != 4:
            raise ValueError("Room name must contain 4 characters")
        if v[1] != "-":
            raise ValueError("Room format must be 'X-YZ'")
        if not v[0].isdigit() or not v[2:4].isdigit():
            raise ValueError("Room format must be 'X-YZ', where X, Y, Z - integers")
        return v


class Group(BaseModel):
    name: str
    number: str

    @classmethod
    @validator("number")
    def number_validate(cls, v: str):
        if len(v) not in [3, 4]:
            raise ValueError("Group number must contain 3 or 4 characters")
        if not v[0:3].isdigit():
            raise ValueError("Group number format must be 'XYZ' or 'XYZM'")
        return v


class Lecturer(BaseModel):
    first_name: str
    middle_name: str
    last_name: str


class Lesson(BaseModel):
    name: str
    room: Room
    group: Group
    lecturer: Lecturer
    start_ts: datetime.time
    end_ts: datetime.time
