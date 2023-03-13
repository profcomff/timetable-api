from .comment import lecturer_comment_router
from .comment_review import lecturer_comment_review_router
from .lecturer import lecturer_router
from .photo import lecturer_photo_router
from .photo_review import lecturer_photo_review_router


__all__ = [
    "lecturer_photo_review_router",
    "lecturer_comment_review_router",
    "lecturer_comment_router",
    "lecturer_router",
    "lecturer_photo_router",
]
