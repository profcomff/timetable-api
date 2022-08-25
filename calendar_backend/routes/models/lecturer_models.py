import datetime

from .base import Base, Lecturer, Event, CommentLecturer


class LecturerWithoutComments(Base):
    id: int
    first_name: str
    middle_name: str
    last_name: str
    avatar_id: int | None
    avatar_link: str | None
    description: str | None


class LecturerWithoutDescription(Base):
    id: int
    first_name: str
    middle_name: str
    last_name: str
    avatar_id: int | None
    avatar_link: str | None
    comments: list[CommentLecturer] | None


class LecturerWithoutDescriptionAndComments(Base):
    id: int
    first_name: str
    middle_name: str
    last_name: str
    avatar_id: int | None
    avatar_link: str | None


class LecturerPhotos(Lecturer):
    links: list[str]


class LecturerPatch(Base):
    first_name: str | None
    middle_name: str | None
    last_name: str | None
    description: str | None

    def __repr__(self):
        return f"Lecturer(first_name={self.first_name}, middle_name={self.middle_name}, last_name={self.last_name})"


class LecturerPost(Base):
    first_name: str
    middle_name: str
    last_name: str
    description: str | None

    def __repr__(self):
        return f"Lecturer(first_name={self.first_name}, middle_name={self.middle_name}, last_name={self.last_name})"


class GetListLecturer(Base):
    items: list[Lecturer]
    limit: int
    offset: int
    total: int


class Photo(Base):
    id: int
    lecturer_id: int
    link: str


class LecturerEvents(Lecturer):
    events: list[Event] = []
