import datetime

from pydantic import BaseModel, validator


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
    def direction_validate(cls, v):
        pass

    @classmethod
    @validator("name")
    def name_validate(cls, v):
        pass


class Group(BaseModel):
    name: str
    number: str

    @classmethod
    @validator("number")
    def number_validate(cls, v):
        pass


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
