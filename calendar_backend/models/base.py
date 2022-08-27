from __future__ import annotations

import re

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Query, Session

from calendar_backend.exceptions import ObjectNotFound


@as_declarative()
class DeclarativeBase:
    """Base class for all database entities"""

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        """Generate database table name automatically.
        Convert CamelCase class name to snake_case db table name.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()


class BaseDbModel(DeclarativeBase):
    __abstract__ = True

    @classmethod
    def create(cls, *, session: Session, **kwargs) -> BaseDbModel:
        obj = cls(**kwargs)
        session.add(obj)
        session.flush()
        return obj

    @classmethod
    def get_all(cls, limit: int | None = 100, offset: int = 0, *, with_deleted: bool = False, session: Session) -> Query[BaseDbModel]:
        """Get all objects with soft deletes"""
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(cls.is_deleted)
        return objs.offset(offset).limit(limit)

    @classmethod
    def get(cls, id: int, *, with_deleted=False, session: Session) -> BaseDbModel:
        """Get object with soft deletes"""
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(cls.is_deleted)
        try:
            return objs.get(id)
        except NoResultFound:
            raise ObjectNotFound(cls, id)

    @classmethod
    def update(cls, id: int, *, session: Session, **kwargs) -> BaseDbModel:
        obj: cls = cls.get(id, session=session)
        for k, v in kwargs.items():
            setattr(obj, k, v)
        session.flush()
        return obj

    @classmethod
    def delete(cls, id: int, *, session: Session) -> None:
        """Soft delete object if possible, else hard delete"""
        obj = cls.get(id, session=session)
        if hasattr(obj, "is_deleted"):
            obj.is_deleted = True
        session.flush()
