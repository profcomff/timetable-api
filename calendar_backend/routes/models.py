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
    pass


class Group(BaseModel):
    pass


class Lecturer(BaseModel):
    pass


class Lesson(BaseModel):
    pass
