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


class TimetableNotFound(NotFound):
    def __init__(self, message: str = "Timetable not found"):
        super().__init__(message)


class GroupTimetableNotFound(TimetableNotFound):
    def __init__(self, group: str):
        message = f"Timetable for group {group} not found"
        super().__init__(message)


class AudienceTimetableNotFound(TimetableNotFound):
    def __init__(self, audience: str):
        message = f"Timetable for audience {audience} not found"
        super().__init__(message)


class TeacherTimetableNotFound(TimetableNotFound):
    def __init__(self, teacher: str):
        message = f"Timetable for teacher {teacher} not found"
        super().__init__(message)
