import datetime

from pydantic import BaseModel


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


class Group(BaseModel):
    name: str
    number: str


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
