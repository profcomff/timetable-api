"""Database common classes and methods"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime
from sqlalchemy import Enum as DbEnum
from sqlalchemy import ForeignKey, Integer, String, Text, and_, or_, true
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import ApproveStatuses, BaseDbModel


class Credentials(BaseDbModel):
    """User credentials"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[JSON] = mapped_column(JSON, nullable=False)
    token: Mapped[JSON] = mapped_column(JSON, nullable=False)
    create_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    update_ts: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Direction(str, Enum):
    NORTH: str = "North"
    SOUTH: str = "South"


class Room(BaseDbModel):
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    direction: Mapped[Direction] = mapped_column(DbEnum(Direction, native_enum=False), nullable=True)
    building: Mapped[str] = mapped_column(String, nullable=True)
    building_url: Mapped[str] = mapped_column(String, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    events: Mapped[list[Event]] = relationship(
        "Event",
        back_populates="room",
        secondary="events_rooms",
        secondaryjoin="and_(Event.id==EventsRooms.event_id, not_(Event.is_deleted))",
        order_by="(Event.start_ts)",
    )


class Lecturer(BaseDbModel):
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    middle_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    avatar_id: Mapped[int] = mapped_column(Integer, ForeignKey("photo.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    avatar: Mapped[Photo] = relationship(
        "Photo",
        foreign_keys="Lecturer.avatar_id",
        backref="is_avatar_for",
        primaryjoin="and_(Lecturer.avatar_id==Photo.id, not_(Photo.is_deleted))",
    )
    photos: Mapped[list[Photo]] = relationship(
        "Photo",
        back_populates="lecturer",
        foreign_keys="Photo.lecturer_id",
        order_by="Photo.id",
        primaryjoin="and_(Lecturer.id==Photo.lecturer_id, not_(Photo.is_deleted), Photo.approve_status=='APPROVED')",
    )
    events: Mapped[list[Event]] = relationship(
        "Event",
        secondary="events_lecturers",
        order_by="(Event.start_ts)",
        back_populates="lecturer",
        secondaryjoin="and_(Event.id==EventsLecturers.event_id, not_(Event.is_deleted))",
    )
    comments: Mapped[list[CommentLecturer]] = relationship(
        "CommentLecturer",
        back_populates="lecturer",
        foreign_keys="CommentLecturer.lecturer_id",
        primaryjoin="and_(Lecturer.id==CommentLecturer.lecturer_id, not_(CommentLecturer.is_deleted), CommentLecturer.approve_status=='APPROVED')",
    )

    @hybrid_method
    def search(self, query: str) -> bool:
        response = true
        query = query.split(' ')
        for q in query:
            response = and_(
                response, or_(self.first_name.contains(q), self.middle_name.contains(q), self.last_name.contains(q))
            )
        return response

    @hybrid_property
    def last_photo(self) -> Photo | None:
        return self.photos[-1] if len(self.photos) else None


class Group(BaseDbModel):
    name: Mapped[str] = mapped_column(String, nullable=False)
    number: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    events: Mapped[list[Event]] = relationship(
        "Event",
        order_by="(Event.start_ts)",
        secondary="events_groups",
        back_populates="group",
        secondaryjoin="and_(Event.id==EventsGroups.event_id, not_(Event.is_deleted))",
    )


class Event(BaseDbModel):
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    room: Mapped[list[Room]] = relationship(
        "Room",
        back_populates="events",
        secondary="events_rooms",
        secondaryjoin="and_(Room.id==EventsRooms.room_id, not_(Room.is_deleted))",
    )
    group: Mapped[list[Group]] = relationship(
        "Group",
        back_populates="events",
        secondary="events_groups",
        secondaryjoin="and_(Group.id==EventsGroups.group_id, not_(Group.is_deleted))",
    )
    lecturer: Mapped[list[Lecturer]] = relationship(
        "Lecturer",
        back_populates="events",
        secondary="events_lecturers",
        secondaryjoin="and_(Lecturer.id==EventsLecturers.lecturer_id, not_(Lecturer.is_deleted))",
    )
    comments: Mapped[list[CommentEvent]] = relationship(
        "CommentEvent",
        foreign_keys="CommentEvent.event_id",
        back_populates="event",
        primaryjoin="and_(Event.id==CommentEvent.event_id, not_(CommentEvent.is_deleted), CommentEvent.approve_status=='APPROVED')",
    )


class EventsLecturers(BaseDbModel):
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("event.id"), nullable=False)
    lecturer_id: Mapped[int] = mapped_column(Integer, ForeignKey("lecturer.id"), nullable=False)


class EventsRooms(BaseDbModel):
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("event.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("room.id"), nullable=False)


class EventsGroups(BaseDbModel):
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("event.id"), nullable=False)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("group.id"), nullable=False)


class Photo(BaseDbModel):
    lecturer_id: Mapped[int] = mapped_column(Integer, ForeignKey("lecturer.id"), nullable=False)
    link: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    approve_status: Mapped[ApproveStatuses] = mapped_column(DbEnum(ApproveStatuses, native_enum=False), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    lecturer: Mapped[Lecturer] = relationship(
        "Lecturer",
        back_populates="photos",
        foreign_keys="Photo.lecturer_id",
        order_by="Lecturer.id",
        primaryjoin="and_(Lecturer.id==Photo.lecturer_id, not_(Lecturer.is_deleted))",
    )


class CommentLecturer(BaseDbModel):
    lecturer_id: Mapped[int] = mapped_column(Integer, ForeignKey("lecturer.id"), nullable=False)
    author_name: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    approve_status: Mapped[ApproveStatuses] = mapped_column(DbEnum(ApproveStatuses, native_enum=False), nullable=False)
    create_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow())
    update_ts: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow(), onupdate=datetime.utcnow()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    lecturer: Mapped[Lecturer] = relationship(
        "Lecturer",
        back_populates="comments",
        foreign_keys="CommentLecturer.lecturer_id",
        primaryjoin="and_(Lecturer.id==CommentLecturer.lecturer_id, not_(Lecturer.is_deleted))",
    )


class CommentEvent(BaseDbModel):
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("event.id"), nullable=False)
    author_name: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    approve_status: Mapped[ApproveStatuses] = mapped_column(DbEnum(ApproveStatuses, native_enum=False), nullable=False)
    create_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow())
    update_ts: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow(), onupdate=datetime.utcnow()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    event: Mapped[Event] = relationship(
        "Event",
        back_populates="comments",
        foreign_keys="CommentEvent.event_id",
        primaryjoin="and_(Event.id==CommentEvent.event_id, not_(Event.is_deleted))",
    )
