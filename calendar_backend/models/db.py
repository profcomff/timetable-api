"""Database common classes and methods
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import JSON

from .base import Base


class Credentials(Base):
    """User credentials"""

    id = Column(Integer, primary_key=True)
    group = Column(String, nullable=False)
    email = Column(String, nullable=False)
    scope = Column(JSON, nullable=False)
    token = Column(JSON, nullable=False)
    create_ts = Column(DateTime, nullable=False, default=datetime.utcnow)
    update_ts = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Timetable(Base):
    """
    Timetable
    """

    start = Column(String, nullable=False)
    end = Column(String, nullable=False)
    odd = Column(Boolean, nullable=False)
    even = Column(Boolean, nullable=False)
    type = Column(String, nullable=False)
    weekday = Column(Integer, nullable=False)
    num = Column(Integer, nullable=False)
    group = Column(String, nullable=False)
    id = Column(String, primary_key=True)
    subject = Column(String, nullable=False)
    place = Column(String, nullable=True)
    teacher = Column(String, nullable=True)
