from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from calendar_backend.models import Lesson

RESOURCE = "/timetable/event/"


def test_create(client_auth: TestClient, dbsession: Session):
    pass


def test_read():
    pass


def test_delete():
    pass


def test_update():
    pass