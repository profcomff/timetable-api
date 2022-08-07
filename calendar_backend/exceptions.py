class NotFound(Exception):
    def __init__(self, message: str = "Object not found"):
        super().__init__(message)


class NoGroupFoundError(NotFound):
    def __init__(self, group: str):
        super().__init__(f"Group :'{group}' not found")


class NoTeacherFoundError(NotFound):
    def __init__(self, teacher: str):
        super().__init__(f"Teacher :'{teacher} not found")


class NoAudienceFoundError(NotFound):
    def __init__(self, audience: str):
        super().__init__(f"Audience :'{audience} not found'")
