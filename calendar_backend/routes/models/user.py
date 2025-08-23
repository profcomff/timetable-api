"""Pydantic models for user-related functionality"""

import datetime
from typing import Literal

from .base import Base


class AttendancePost(Base):
    """Request to mark attendance for an event"""
    status: Literal["attending", "not_attending", "maybe"] = "attending"


class AttendanceGet(Base):
    """Attendance information response"""
    id: int
    user_id: int
    event_id: int
    status: Literal["attending", "not_attending", "maybe"]
    create_ts: datetime.datetime
    update_ts: datetime.datetime


class AttendanceListGet(Base):
    """List of attendees for an event"""
    event_id: int
    total_attendees: int
    attendances: list[AttendanceGet]


class SubscriptionPost(Base):
    """Request to create a calendar subscription"""
    subscription_type: Literal["group", "lecturer", "room"]
    target_id: int


class SubscriptionGet(Base):
    """Calendar subscription response"""
    id: int
    user_id: int
    subscription_type: Literal["group", "lecturer", "room"]
    target_id: int
    is_active: bool
    create_ts: datetime.datetime
    update_ts: datetime.datetime


class UserSubscriptionsGet(Base):
    """User's calendar subscriptions"""
    user_id: int
    subscriptions: list[SubscriptionGet]


class PersonalEventPost(Base):
    """Request to create a personal event"""
    name: str
    start_ts: datetime.datetime
    end_ts: datetime.datetime
    description: str | None = None


class PersonalEventGet(Base):
    """Personal event response"""
    id: int
    name: str
    start_ts: datetime.datetime
    end_ts: datetime.datetime
    creator_user_id: int
    is_personal: bool = True
    description: str | None = None
    create_ts: datetime.datetime
    update_ts: datetime.datetime


class UserCalendarGet(Base):
    """User's personal calendar"""
    user_id: int
    events: list[PersonalEventGet]
    subscribed_events: list[dict]  # Events from subscriptions