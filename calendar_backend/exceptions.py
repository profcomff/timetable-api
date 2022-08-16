class NotFound(Exception):
    def __init__(self, message: str = "Object not found"):
        super().__init__(message)


class NoGroupFoundError(NotFound):
    def __init__(self, group: int):
        super().__init__(f"Group :'{group}' not found")


class NoTeacherFoundError(NotFound):
    def __init__(self, teacher: int):
        super().__init__(f"Teacher :'{teacher} not found")


class NoAudienceFoundError(NotFound):
    def __init__(self, audience: int):
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


class EventNotFound(NotFound):
    def __init__(self, id: int):
        message = f"Event {id} not found"
        super().__init__(message)


class GroupsNotFound(NotFound):
    def __init__(self):
        message = f"Groups list not found"
        super().__init__(message)


class RoomsNotFound(NotFound):
    def __init__(self):
        message = f"Rooms list not found"
        super().__init__(message)


class LecturersNotFound(NotFound):
    def __init__(self):
        message = f"Lecturers list not found"
        super().__init__(message)


class LessonsNotFound(NotFound):
    def __init__(self):
        message = f"Lessons list not found"
        super().__init__(message)