from .base import LecturerGet, CommentLecturer, CommentEventGet, EventGet, GroupGet, RoomGet
from .lecturer import (
    LecturerPost,
    LecturerPatch,
    LecturerPhotos,
    LecturerEvents,
    GetListLecturer,
    Photo,
    LecturerCommentPost,
    LecturerCommentPatch,
    LecturerComments,
    Action,
)
from .room import RoomPost, RoomPatch, RoomEvents, GetListRoom
from .event import EventPost, EventPatch, Event, GetListEvent, EventComments
from .group import GroupPost, GroupPatch, GroupEvents, GetListGroup
