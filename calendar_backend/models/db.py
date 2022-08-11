"""Database common classes and methods
"""
from __future__ import annotations

import enum
from datetime import datetime

import sqlalchemy.orm
from sqlalchemy import Column

from .base import Base


class Credentials(Base):
    """User credentials"""

    id = Column(sqlalchemy.Integer, primary_key=True)
    group = Column(sqlalchemy.String, nullable=False)
    email = Column(sqlalchemy.String, nullable=False)
    scope = Column(sqlalchemy.JSON, nullable=False)
    token = Column(sqlalchemy.JSON, nullable=False)
    create_ts = Column(sqlalchemy.DateTime, nullable=False, default=datetime.utcnow)
    update_ts = Column(sqlalchemy.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Direction(str, enum.Enum):
    NORTH: str = "North"
    SOUTH: str = "South"


class LectureRooms(str, enum.Enum):
    NPA: str = "СФА"
    CPA: str = "ЦФА"
    SPA: str = "ЮФА"


class Room(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    direction = sqlalchemy.Column(sqlalchemy.Enum(Direction.SOUTH, Direction.NORTH), nullable=False)
    lessons: list[Lesson] = sqlalchemy.orm.relationship(
        "Lesson", foreign_keys="Lesson.room_id", order_by="(Lesson.start_ts)"
    )

    def __repr__(self):
        return f"Room:{self.name}, direction:{self.direction}"


class Lecturer(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    first_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    middle_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    last_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    lessons: list[Lesson] = sqlalchemy.orm.relationship(
        "Lesson", foreign_keys="Lesson.lecturer_id", order_by="(Lesson.start_ts)"
    )

    def __repr__(self):
        return f"Lecturer's name:{self.name}, middle name:{self.middle_name}, last name:{self.last_name}"


class Group(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    number = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    lessons: list[Lesson] = sqlalchemy.orm.relationship(
        "Lesson", foreign_keys="Lesson.group_id", order_by="(Lesson.start_ts)"
    )

    def __repr__(self):
        return f"Group number:{self.number}"


class Lesson(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    room_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("room.id"))
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("group.id"))
    lecturer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lecturer.id"))
    start_ts = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    end_ts = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    room: Room = sqlalchemy.orm.relationship("Room", foreign_keys="Lesson.room_id", back_populates="lessons")
    group: Group = sqlalchemy.orm.relationship("Group", foreign_keys="Lesson.group_id", back_populates="lessons")
    lecturer: Lecturer = sqlalchemy.orm.relationship(
        "Lecturer", foreign_keys="Lesson.lecturer_id", back_populates="lessons"
    )

    def __repr__(self):
        return (
            f"Lesson:{self.name}, room:{self.room.name}, group:{self.group.number},"
            f" lecturer:{self.lecturer.__repr__()}"
        )

