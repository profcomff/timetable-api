import re
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Query


class CustomQuery(Query):
    def __new__(cls, *args, **kwargs):
        if args and hasattr(args[0][0], "is_deleted"):
            return Query(*args, **kwargs).filter_by(is_deleted=False)
        else:
            return object.__new__(cls)


@as_declarative()
class Base:
    """Base class for all database entities"""

    query_class = CustomQuery

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        """Generate database table name automatically.
        Convert CamelCase class name to snake_case db table name.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
