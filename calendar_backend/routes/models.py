import datetime

from pydantic import BaseModel, validator

from calendar_backend.models import Direction, LectureRooms


class Base(BaseModel):
    class Config:
        orm_mode = True


class Room(Base):
    name: str
    direction: str

    @classmethod
    @validator("direction")
    def direction_validate(cls, v: str):
        if v not in [Direction.SOUTH, Direction.NORTH]:
            raise ValueError(f"Direction must be either {Direction.NORTH} or {Direction.SOUTH}")
        return v

    @classmethod
    @validator("name")
    def name_validate(cls, v: str):
        if v in [LectureRooms.CPA, LectureRooms.NPA, LectureRooms.SPA]:
            return v
        if len(v) != 4:
            raise ValueError("Room name must contain 4 characters")
        if v[1] != "-":
            raise ValueError("Room format must be 'X-YZ'")
        if not v[0].isdigit() or not v[2:4].isdigit():
            raise ValueError("Room format must be 'X-YZ', where X, Y, Z - integers")
        return v

    def __repr__(self):
        return f"<Room name:{self.name}, direction:{self.direction}"


class Group(Base):
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
        return f"<Group number:{self.number}, name:{self.name}>"


class Lecturer(Base):
    first_name: str
    middle_name: str
    last_name: str

    def __repr__(self):
        return f"<Lecturer first_name:{self.first_name}, middle_name:{self.middle_name}, last_name:{self.last_name}>"


class Lesson(Base):
    name: str
    room: Room
    group: Group
    lecturer: Lecturer
    start_ts: datetime.datetime
    end_ts: datetime.datetime

    def __repr__(self):
        return (
            f"<Lesson name:{self.name}, room:{self.room}, group:{self.group}"
            f", lecturer:{self.lecturer}, start_ts:{self.start_ts}, end_ts:{self.end_ts}"
        )
