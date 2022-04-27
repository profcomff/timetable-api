"""Database common classes and methods
"""
import os
import re
from datetime import datetime
from typing import Any
from sqlalchemy import *

import psycopg2
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class BaseModel:
    """Base class for all database entities"""

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        """Generate database table name automatically.

        Convert CamelCase class name to snake_case db table name.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()


class Credentials(BaseModel):
    """User credentials"""
    id = Column(Integer, primary_key=True)
    group = Column(String, nullable=False)
    email = Column(String, nullable=False)
    scope = Column(JSON, nullable=False)
    token = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Timetable(BaseModel):
    start = Column(String, nullable=False)
    end = Column(String, nullable=False)
    odd = Column(Boolean, nullable=False)
    even = Column(Boolean, nullable=False)
    type = Column(String, nullable=False)
    weekday = Column(Integer, nullable=False)
    num = Column(Integer, nullable=False)
    group = Column(String, nullable=False)
    id = Column(String, nullable=False, primary_key=True)
    subject = Column(String, nullable=False)
    place = Column(String, nullable=True)
    teacher = Column(String, nullable=True)
