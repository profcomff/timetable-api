from typing import Type


class ObjectNotFound(Exception):
    def __init__(self, type: Type, ids: int | list[int]):
        super().__init__(f"Objects of type {type.__name__} {ids=} not found")


class NotEnoughCriteria(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ForbiddenAction(Exception):
    def __init__(self, type: Type, id: int):
        super().__init__(f"Forbidden action with {type.__name__}, {id=}")
