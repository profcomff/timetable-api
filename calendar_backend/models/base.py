import re
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound


@as_declarative()
class Base:
    """Base class for all database entities"""

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        """Generate database table name automatically.
        Convert CamelCase class name to snake_case db table name.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    @classmethod
    def get_all(cls, *, with_deleted=False, session: Session):
        """Get all objects with soft deletes
        """
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(cls.is_deleted)
        return objs

    @classmethod
    def get(cls, id: int, *, with_deleted=False, session: Session):
        """Get object with soft deletes
        """
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(cls.is_deleted)
        try:
            return objs.get(id)
        except NoResultFound:
            return None

    def delete(self, id: int):
        """Soft delete object if possible, else hard delete
        """
        if hasattr(self, "is_deleted"):
            self.is_deleted = True
