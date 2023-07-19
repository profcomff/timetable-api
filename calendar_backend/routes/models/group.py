from pydantic import field_validator

from .base import Base, EventGet, GroupGet


class GroupPatch(Base):
    name: str | None = None
    number: str | None = None

    @classmethod
    @field_validator("number")
    def number_validate(cls, v: str):
        if v is None:
            return v
        if len(v) not in [3, 4]:
            raise ValueError("Group number must contain 3 or 4 characters")
        if not v[0:3].isdigit():
            raise ValueError("Group number format must be 'XYZ' or 'XYZM'")
        return v

    def __repr__(self):
        return f"Group(name={self.name}, number={self.number})"


class GroupPost(Base):
    name: str | None = None
    number: str

    @classmethod
    @field_validator("number")
    def number_validate(cls, v: str):
        if v is None:
            return v
        if len(v) not in [3, 4]:
            raise ValueError("Group number must contain 3 or 4 characters")
        if not v[0:3].isdigit():
            raise ValueError("Group number format must be 'XYZ' or 'XYZM'")
        return v

    def __repr__(self):
        return f"Group(name={self.name}, number={self.number})"


class GetListGroup(Base):
    items: list[GroupGet]
    limit: int
    offset: int
    total: int


class GroupEvents(GroupGet):
    events: list[EventGet]
