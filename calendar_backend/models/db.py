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
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    direction = sqlalchemy.Column(sqlalchemy.Enum("North", "South", name="Directions"), nullable=True)
    lessons: list[Lesson] = sqlalchemy.orm.relationship(
        "Lesson", back_populates="room", secondary="lessons_rooms", order_by="(Lesson.start_ts)"
    )

    def __repr__(self):
        return f"Room(id={self.id}, name={self.name}, direction={self.direction})"


class Lecturer(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    first_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    middle_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    last_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    lessons: list[Lesson] = sqlalchemy.orm.relationship(
        "Lesson", secondary="lessons_lecturers", order_by="(Lesson.start_ts)", back_populates="lecturer"
    )

    def __repr__(self):
        return f"Lecturer(id={self.id}, first_name={self.first_name}, middle_name={self.middle_name}, last_name={self.last_name})"


class Group(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    number = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    lessons: list[Lesson] = sqlalchemy.orm.relationship(
        "Lesson", foreign_keys="Lesson.group_id", order_by="(Lesson.start_ts)"
    )

    def __repr__(self):
        return f"Group(id={self.id}, name={self.name}, number={self.number})"


class Lesson(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("group.id"))
    start_ts = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    end_ts = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    room: Room = sqlalchemy.orm.relationship(
        "Room", back_populates="lessons", secondary="lessons_rooms"
    )
    group: Group = sqlalchemy.orm.relationship(
        "Group", foreign_keys="Lesson.group_id", back_populates="lessons"
    )
    lecturer: Lecturer = sqlalchemy.orm.relationship(
        "Lecturer", back_populates="lessons", secondary="lessons_lecturers"
    )

    def __repr__(self):
        return (
            f"Lesson(id={self.id}, name={self.name},"
            f" room={self.room}, group={self.group},"
            f" lecturer={self.lecturer}, start_ts={self.start_ts}, end_ts={self.end_ts})"
        )


class LessonsLecturers(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    lesson_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lesson.id"))
    lecturer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lecturer.id"))


class LessonsRooms(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    lesson_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lesson.id"))
    room_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("room.id"))
