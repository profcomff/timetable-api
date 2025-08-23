"""Webhook system for calendar synchronization"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Any

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from calendar_backend.models.base import BaseDbModel

logger = logging.getLogger(__name__)


class WebhookEventType(str, Enum):
    EVENT_CREATED = "event.created"
    EVENT_UPDATED = "event.updated" 
    EVENT_DELETED = "event.deleted"
    ATTENDANCE_MARKED = "attendance.marked"
    SUBSCRIPTION_CREATED = "subscription.created"


class WebhookStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


class Webhook(BaseDbModel):
    """Webhook registration for external calendar synchronization"""
    
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    secret: Mapped[str] = mapped_column(String, nullable=False)  # For webhook signature verification
    event_types: Mapped[list] = mapped_column(JSON, nullable=False)  # List of WebhookEventType values
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    create_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    update_ts: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class WebhookDelivery(BaseDbModel):
    """Webhook delivery log"""
    
    webhook_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    event_type: Mapped[WebhookEventType] = mapped_column(String, nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[WebhookStatus] = mapped_column(String, nullable=False, default=WebhookStatus.PENDING)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    last_attempt_ts: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    response_status: Mapped[int] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str] = mapped_column(String, nullable=True)
    create_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)