from typing import Type


class ObjectNotFound(Exception):
    def __init__(self, type: Type, id: int):
        super().__init__(f"Object {type.__name__} {id=} not found")


class NotEnoughCriteria(Exception):
    pass


class ForbiddenAction(Exception):
    def __init__(self, type: Type, id: int):
        super().__init__(f"Forbidden action with {type.__name__}, {id=}")
