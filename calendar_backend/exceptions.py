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


class PhotoNotFoundError(NotFound):
    def __init__(self, id: int):
        message = f"Photo {id} not found"
        super().__init__(message)


class LecturerPhotoNotFoundError(PhotoNotFoundError):
    def __init__(self, id: int, lecturer_id: int):
        message = f"Photo {id} of lecturer {lecturer_id} not found"
        super(PhotoNotFoundError, self).__init__(message)
