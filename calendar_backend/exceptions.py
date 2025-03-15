from typing import Type


class ObjectNotFound(Exception):
    def __init__(self, type: Type, ids: int | list[int] = [], name: str | None = None):
        msg = f"Objects of type {type.__name__} {ids=} not found"
        if name:
            msg = f"Objects of type {type.__name__} with {name=} not found"
        super().__init__(msg)


class NotEnoughCriteria(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ForbiddenAction(Exception):
    def __init__(self, type: Type, id: int):
        super().__init__(f"Forbidden action with {type.__name__}, {id=}")
