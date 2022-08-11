import datetime

from fastapi import APIRouter

from calendar_backend import get_settings
from calendar_backend.routes.models import Room, Group, Lecturer, Lesson
from calendar_backend.methods import utils

cud_router = APIRouter(prefix="/auth-nedeed/timetable/", tags=["CUD"])
settings = get_settings()


@cud_router.post("/create/room/", response_model=Room)
async def http_create_room(room: Room) -> Room:
    pass


@cud_router.post("/create/group/", response_model=Group)
async def http_create_group(group: Group) -> Group:
    pass


@cud_router.post("/create/lecturer/", response_model=Lecturer)
async def http_create_lecturer(lecturer: Lecturer) -> Lecturer:
    pass


@cud_router.post("/create/lesson/", response_model=Lesson)
async def http_create_lesson(lesson: Lesson) -> Lesson:
    pass


@cud_router.patch("/patch/room/", response_model=Room)
async def http_patch_room(room: Room, new_name: str | None = None) -> Room:
    pass


@cud_router.patch("/patch/group/", response_model=Group)
async def http_patch_group(group: Group, new_number: str | None = None, new_name: str | None = None) -> Group:
    pass


@cud_router.patch("/patch/lecturer", response_model=Lecturer)
async def http_patch_lecturer(
    lecturer: Lecturer,
    new_first_name: str | None = None,
    new_middle_name: str | None = None,
    new_last_name: str | None = None,
) -> Lecturer:
    pass


@cud_router.patch("/patch/lesson/", response_model=Lesson)
async def http_patch_lesson(
    lesson: Lesson,
    new_name: str | None = None,
    new_room: Room | None = None,
    new_group: Group | None = None,
    new_lecturer: Lecturer | None = None,
    new_start_ts: datetime.datetime | None = None,
    new_end_ts: datetime.datetime | None = None,
) -> Lesson:
    pass


@cud_router.delete("/delete/room/")
async def http_delete_room(room: Room) -> None:
    pass


@cud_router.delete("/delete/lecturer/")
async def http_delete_lecturer(lecturer: Lecturer) -> None:
    pass


@cud_router.delete("/delete/group/")
async def http_delete_group(group: Group) -> None:
    pass


@cud_router.delete("/delete/lesson/")
async def http_delete_lesson(lesson: Lesson) -> None:
    pass
