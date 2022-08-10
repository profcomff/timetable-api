import enum

import sqlalchemy.orm

from .base import Base


class Direction(enum.Enum, str):
    NORTH = "North"
    SOUTH = "South"


class Room(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    direction = sqlalchemy.Column(sqlalchemy.Enum, nullable=False)

    def __repr__(self):
        return f"Room:{self.name}, direction:{self.direction}"


class Lecturer(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    first_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    middle_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    last_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return f"Lecturer's name:{self.name}, middle name:{self.middle_name}, last name:{self.last_name}"


class Group(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    number = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return f"Group number:{self.number}"


class Lesson(Base):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    room_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("room.id"))
    groud_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("group.id"))
    lecturer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lecturer.id"))
    start_ts = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    end_ts = sqlalchemy.Column(sqlalchemy.Time, nullable=False)

    room: Room = sqlalchemy.orm.relationship("room", foreign_keys="lesson.room_id")
    group: Group = sqlalchemy.orm.relationship("group", foreign_keys="lesson.group_id")
    lecturer: Lecturer = sqlalchemy.orm.relationship("lecturer", foreign_keys="lesson.lecturer_id")

    def __repr__(self):
        return f"Lesson:{self.name}, room:{self.room.name}, group:{self.group.number}," \
               f" lecturer:{self.lecturer.__repr__()}"
