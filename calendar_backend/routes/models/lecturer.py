from calendar_backend.models import ApproveStatuses

from .base import Base, CommentLecturer, EventGet, LecturerGet


class LecturerPhotos(Base):
    items: list[str]
    limit: int
    offset: int
    total: int


class LecturerPatch(Base):
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    avatar_id: int | None = None
    description: str | None = None

    def __repr__(self):
        return f"Lecturer(first_name={self.first_name}, middle_name={self.middle_name}, last_name={self.last_name})"


class LecturerPost(Base):
    first_name: str
    middle_name: str
    last_name: str
    description: str | None = None

    def __repr__(self):
        return f"Lecturer(first_name={self.first_name}, middle_name={self.middle_name}, last_name={self.last_name})"


class GetListLecturer(Base):
    items: list[LecturerGet]
    limit: int
    offset: int
    total: int


class Photo(Base):
    id: int
    lecturer_id: int
    link: str


class LecturerEvents(LecturerGet):
    events: list[EventGet]


class LecturerCommentPost(Base):
    author_name: str
    text: str


class LecturerCommentPatch(Base):
    author_name: str | None = None
    text: str | None = None


class LecturerComments(Base):
    items: list[CommentLecturer]
    limit: int
    offset: int
    total: int


class Action(Base):
    action: ApproveStatuses
