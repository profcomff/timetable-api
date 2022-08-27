from .base import Base, LecturerGet, EventGet


class LecturerPhotos(Base):
    id: int
    links: list[str]
    limit: int
    offset: int
    total: int


class LecturerPatch(Base):
    first_name: str | None
    middle_name: str | None
    last_name: str | None
    description: str | None
    is_deleted: bool | None

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
    items: list[LecturerGet]
    limit: int
    offset: int
    total: int


class Photo(Base):
    id: int
    lecturer_id: int
    link: str


class LecturerEvents(LecturerGet):
    events: list[EventGet] = []


class CommentLecturerPost(Base):
    author_name: str
    text: str


class CommentLecturerPatch(Base):
    author_name: str | None
    text: str | None