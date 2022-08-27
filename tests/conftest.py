from datetime import datetime
import os.path

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from calendar_backend.models.base import Base
from calendar_backend.models.db import CommentsLecturer, Group, Lecturer, Photo, Room
from calendar_backend.routes import app
from calendar_backend.settings import get_settings


@pytest.fixture()
def client():
    client = TestClient(app)
    return client


@pytest.fixture()
def client_auth(mocker: MockerFixture):
    client = TestClient(app)
    access_token = client.post(f"/token", {"username": "admin", "password": "42"}).json()["access_token"]
    client.headers = {"Authorization": f"Bearer {access_token}"}
    return client


@pytest.fixture()
def dbsession():
    settings = get_settings()
    engine = create_engine(settings.DB_DSN)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


@pytest.fixture()
def room_path(client_auth: TestClient, dbsession: Session):
    RESOURCE = "/timetable/room/"
    request_obj = {
        "name": datetime.now().isoformat(),
        "direction": "North",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    id_ = response.json()["id"]
    yield RESOURCE + "{id_}"
    response_model: Room = dbsession.query(Room).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def group_path(client_auth: TestClient, dbsession: Session):
    RESOURCE = "/timetable/group/"
    request_obj = {
        "name": "",
        "number": datetime.now().isoformat(),
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    id_ = response.json()["id"]
    yield RESOURCE + "{id_}"
    response_model: Group = dbsession.query(Group).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def lecturer_path(client_auth: TestClient, dbsession: Session):
    RESOURCE = "/timetable/lecturer/"
    request_obj = {
        "first_name": "Петр",
        "middle_name": "Васильевич",
        "last_name": "Тритий",
        "description": "Очень умный",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    id_ = response.json()["id"]
    yield f"/timetable/lecturer/{id_}"
    response_model: Lecturer = dbsession.query(Lecturer).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def comment_path(client_auth: TestClient, dbsession: Session, lecturer_path: int):
    RESOURCE = f"{lecturer_path}/comment"
    request_obj = {
        "author_name": "Аноним",
        "comment_text": "Очень умный коммент",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    id_ = response.json()["id"]
    yield f"{lecturer_path}/comment/{id_}"
    response_model: CommentsLecturer = dbsession.query(CommentsLecturer).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def photo_path(client_auth: TestClient, dbsession: Session, lecturer_path: int):
    RESOURCE = f"{lecturer_path}/photo"
    with open(os.path.dirname(__file__) + "/photo.png", "rb") as f:
        response = client_auth.post(RESOURCE, files={"photo": f})
    assert response.ok, response.json()
    id_ = response.json()["id"]
    yield f"{lecturer_path}/photo/{id_}"
    response_model: CommentsLecturer = dbsession.query(Photo).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()
