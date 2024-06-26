from __future__ import annotations

import re
from enum import Enum

from sqlalchemy import Integer, not_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, Query, Session, mapped_column

from calendar_backend.exceptions import ObjectNotFound


class ApproveStatuses(str, Enum):
    APPROVED: str = "Approved"
    DECLINED: str = "Declined"
    PENDING: str = "Pending"


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
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __repr__(self):
        attrs = []
        for c in self.__table__.columns:
            attrs.append(f"{c.name}={getattr(self, c.name)}")
        return "{}({})".format(c.__class__.__name__, ', '.join(attrs))

    @classmethod
    def create(cls, *, session: Session, **kwargs) -> BaseDbModel:
        obj = cls(**kwargs)
        session.add(obj)
        session.flush()
        return obj

    @classmethod
    def get_all(cls, *, with_deleted: bool = False, only_approved: bool = True, session: Session) -> Query:
        """Get all objects with soft deletes"""
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(not_(cls.is_deleted))
        if only_approved and hasattr(cls, "approve_status"):
            objs = objs.filter(cls.approve_status == ApproveStatuses.APPROVED)
        return objs

    @classmethod
    def get(cls, id: int, *, with_deleted=False, only_approved: bool = True, session: Session) -> BaseDbModel:
        """Get object with soft deletes"""
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(not_(cls.is_deleted))
        if only_approved and hasattr(cls, "approve_status"):
            objs = objs.filter(cls.approve_status == ApproveStatuses.APPROVED)
        try:
            return objs.filter(cls.id == id).one()
        except NoResultFound:
            raise ObjectNotFound(cls, id)

    @classmethod
    def update(cls, id: int, *, session: Session, **kwargs) -> BaseDbModel:
        obj: cls = cls.get(id, only_approved=False, session=session)
        for k, v in kwargs.items():
            setattr(obj, k, v)
        session.flush()
        return obj

    @classmethod
    def delete(cls, id: int, *, session: Session) -> None:
        """Soft delete object if possible, else hard delete"""
        obj = cls.get(id, only_approved=False, session=session)
        if hasattr(obj, "is_deleted"):
            obj.is_deleted = True
        else:
            session.delete(obj)
        session.flush()
