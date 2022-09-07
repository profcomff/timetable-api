"""Database common classes and methods
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Enum as DbEnum
from sqlalchemy import and_, or_
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship

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


class ApproveStatuses(str, Enum):
    APPROVED: str = "Approved"
    DECLINED: str = "Declined"


class Room(BaseDbModel):
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    direction = sqlalchemy.Column(DbEnum(Direction, native_enum=False), nullable=True)
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    events: list[Event] = relationship(
        "Event",
        back_populates="room",
        secondary="events_rooms",
        secondaryjoin="and_(Event.id==EventsRooms.event_id, not_(Event.is_deleted))",
        order_by="(Event.start_ts)",
    )


class Lecturer(BaseDbModel):
    first_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    middle_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    last_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    avatar_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("photo.id"))
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    avatar: Photo = relationship(
        "Photo",
        foreign_keys="Lecturer.avatar_id",
        backref="is_avatar_for",
        primaryjoin="and_(Lecturer.avatar_id==Photo.id, not_(Photo.is_deleted))",
    )
    photos: list[Photo] = relationship(
        "Photo",
        back_populates="lecturer",
        foreign_keys="Photo.lecturer_id",
        order_by="Photo.id",
        primaryjoin="and_(Lecturer.id==Photo.lecturer_id, not_(Photo.is_deleted))",
    )
    events: list[Event] = relationship(
        "Event",
        secondary="events_lecturers",
        order_by="(Event.start_ts)",
        back_populates="lecturer",
        secondaryjoin="and_(Event.id==EventsLecturers.event_id, not_(Event.is_deleted))",
    )
    comments: list[CommentLecturer] = relationship(
        "CommentLecturer",
        back_populates="lecturer",
        foreign_keys="CommentLecturer.lecturer_id",
        primaryjoin="and_(Lecturer.id==CommentLecturer.lecturer_id, not_(CommentLecturer.is_deleted))",
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

    events: list[Event] = relationship(
        "Event",
        foreign_keys="Event.group_id",
        order_by="(Event.start_ts)",
        primaryjoin="and_(Group.id==Event.group_id, not_(Event.is_deleted))",
    )


class Event(BaseDbModel):
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("group.id"))
    start_ts = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    end_ts = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    room: list[Room] = relationship(
        "Room",
        back_populates="events",
        secondary="events_rooms",
        secondaryjoin="and_(Room.id==EventsRooms.room_id, not_(Room.is_deleted))",
    )
    group: Group = relationship(
        "Group",
        back_populates="events",
        foreign_keys="Event.group_id",
        primaryjoin="and_(Group.id==Event.group_id, not_(Group.is_deleted))",
    )
    lecturer: list[Lecturer] = relationship(
        "Lecturer",
        back_populates="events",
        secondary="events_lecturers",
        secondaryjoin="and_(Lecturer.id==EventsLecturers.lecturer_id, not_(Lecturer.is_deleted))",
    )
    comments: list[CommentEvent] = relationship(
        "CommentEvent",
        foreign_keys="CommentEvent.event_id",
        back_populates="event",
        primaryjoin="and_(Event.id==CommentEvent.event_id, not_(CommentEvent.is_deleted))",
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
    approve_status = sqlalchemy.Column(DbEnum(ApproveStatuses, native_enum=False), nullable=True)
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    lecturer: Lecturer = relationship(
        "Lecturer",
        back_populates="photos",
        foreign_keys="Photo.lecturer_id",
        order_by="Lecturer.id",
        primaryjoin="and_(Lecturer.id==Photo.lecturer_id, not_(Lecturer.is_deleted))",
    )


class CommentLecturer(BaseDbModel):
    lecturer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lecturer.id"))
    author_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    approve_status = sqlalchemy.Column(DbEnum(ApproveStatuses, native_enum=False), nullable=True)
    create_ts = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow())
    update_ts = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    lecturer: Lecturer = relationship(
        "Lecturer",
        back_populates="comments",
        foreign_keys="CommentLecturer.lecturer_id",
        primaryjoin="and_(Lecturer.id==CommentLecturer.lecturer_id, not_(Lecturer.is_deleted))",
    )


class CommentEvent(BaseDbModel):
    event_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("event.id"))
    author_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    approve_status = sqlalchemy.Column(DbEnum(ApproveStatuses, native_enum=False), nullable=True)
    create_ts = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow())
    update_ts = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    event: Event = relationship(
        "Event",
        back_populates="comments",
        foreign_keys="CommentEvent.event_id",
        primaryjoin="and_(Event.id==CommentEvent.event_id, not_(Event.is_deleted))",
    )
