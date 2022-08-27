"""Database common classes and methods
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

import sqlalchemy.orm
from sqlalchemy import Column, Enum as DbEnum, and_, or_
from sqlalchemy.ext.hybrid import hybrid_method

from .base import BaseDbModel


class Credentials(BaseDbModel):
    """User credentials"""

    id = Column(sqlalchemy.Integer, primary_key=True)
    group = Column(sqlalchemy.String, nullable=False)
    email = Column(sqlalchemy.String, nullable=False)
    scope = Column(sqlalchemy.JSON, nullable=False)
    token = Column(sqlalchemy.JSON, nullable=False)
    create_ts = Column(sqlalchemy.DateTime, nullable=False, default=datetime.utcnow)
    update_ts = Column(sqlalchemy.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Direction(str, Enum):
    NORTH: str = "North"
    SOUTH: str = "South"


class Room(BaseDbModel):
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    direction = sqlalchemy.Column(DbEnum(Direction, native_enum=False), nullable=True)
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    events: list[Event] = sqlalchemy.orm.relationship(
        "Event", back_populates="room", secondary="events_rooms", order_by="(Event.start_ts)"
    )


class Lecturer(BaseDbModel):
    first_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    middle_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    last_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    avatar_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("photo.id"))
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    avatar: Photo = sqlalchemy.orm.relationship("Photo", foreign_keys="Lecturer.avatar_id")
    photos: list[Photo] = sqlalchemy.orm.relationship(
        "Photo", foreign_keys="Photo.lecturer_id", order_by="Photo.id", back_populates="lecturer"
    )

    events: list[Event] = sqlalchemy.orm.relationship(
        "Event", secondary="events_lecturers", order_by="(Event.start_ts)", back_populates="lecturer"
    )

    comments: list[CommentLecturer] = sqlalchemy.orm.relationship(
        "CommentLecturer", foreign_keys="CommentLecturer.lecturer_id", back_populates="lecturer"
    )

    @hybrid_method
    def search(self, query: str) -> bool:
        response = sqlalchemy.true
        query = query.split(' ')
        for q in query:
            response = and_(
                response, or_(self.first_name.contains(q), self.middle_name.contains(q), self.last_name.contains(q))
            )
        return response


class Group(BaseDbModel):
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    number = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    events: list[Event] = sqlalchemy.orm.relationship(
        "Event", foreign_keys="Event.group_id", order_by="(Event.start_ts)"
    )


class Event(BaseDbModel):
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("group.id"))
    start_ts = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    end_ts = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    room: list[Room] = sqlalchemy.orm.relationship("Room", back_populates="events", secondary="events_rooms")
    group: Group = sqlalchemy.orm.relationship("Group", foreign_keys="Event.group_id", back_populates="events")
    lecturer: list[Lecturer] = sqlalchemy.orm.relationship(
        "Lecturer", back_populates="events", secondary="events_lecturers"
    )

    comments: list[CommentEvent] = sqlalchemy.orm.relationship(
        "CommentEvent", foreign_keys="CommentEvent.event_id", back_populates="event"
    )


class EventsLecturers(BaseDbModel):
    event_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("event.id"))
    lecturer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lecturer.id"))


class EventsRooms(BaseDbModel):
    event_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("event.id"))
    room_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("room.id"))


class Photo(BaseDbModel):
    lecturer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lecturer.id"))
    link = sqlalchemy.Column(sqlalchemy.String, unique=True)
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    lecturer: Lecturer = sqlalchemy.orm.relationship(
        "Lecturer", foreign_keys="Photo.lecturer_id", order_by="Lecturer.id", back_populates="photos"
    )


class CommentLecturer(BaseDbModel):
    lecturer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lecturer.id"))
    author_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    create_ts = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow())
    update_ts = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    lecturer: Lecturer = sqlalchemy.orm.relationship(
        "Lecturer", foreign_keys="CommentLecturer.lecturer_id", back_populates="comments"
    )


class CommentEvent(BaseDbModel):
    event_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("event.id"))
    author_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    create_ts = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow())
    update_ts = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    event: Event = sqlalchemy.orm.relationship("Event", foreign_keys="CommentEvent.event_id", back_populates="comments")
