"""Database common classes and methods
"""
import re
from datetime import datetime
from typing import Any

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
    code = Column(String, nullable=False)
    scope = Column(JSON, nullable=False)
    group = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    authuser = Column(Integer, nullable=False)
    hd = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
