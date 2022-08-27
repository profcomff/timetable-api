from typing import Type


class ObjectNotFound(Exception):
    def __init__(self, type: Type, id):
        super().__init__(f"Objet {type.__name__} {id=} not found")
