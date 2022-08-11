from fastapi import APIRouter

from calendar_backend import get_settings

cud_router = APIRouter(prefix="/auth-nedeed/timetable/", tags=["CUD"])
settings = get_settings()

