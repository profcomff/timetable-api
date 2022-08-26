from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from calendar_backend.models import Group

RESOURCE = "/timetable/event/"