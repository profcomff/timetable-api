from .base import LecturerGet, CommentLecturer, CommentEventGet, EventGet, GroupGet, RoomGet
from .lecturer import (
    LecturerGet,
    LecturerPost,
    LecturerPatch,
    LecturerPhotos,
    LecturerEvents,
    GetListLecturer,
    Photo,
    CommentLecturerPost,
    CommentLecturerPatch,
    LecturerComments
)
from .room import RoomPost, RoomPatch, RoomEvents, GetListRoom
from .event import (
    EventPost,
    EventPatch,
    Event,
    GetListEvent,
    CommentEventGet,
)
from .group import GroupPost, GroupPatch, GroupEvents, GetListGroup
