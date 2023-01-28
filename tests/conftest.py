import os.path
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from starlette import status

from calendar_backend.models.base import DeclarativeBase
from calendar_backend.models.db import CommentLecturer, Event, Group, Lecturer, Photo, Room
from calendar_backend.routes import app
from calendar_backend.settings import get_settings


@pytest.fixture()
def client():
    client = TestClient(app)
    return client


@pytest.fixture()
def client_auth(mocker: MockerFixture):
    client = TestClient(app)
    access_token = client.post(f"/token", data={"username": "admin", "password": "42"}).json()["access_token"]
    client.headers = {"Authorization": f"Bearer {access_token}"}
    return client


@pytest.fixture()
def dbsession():
    settings = get_settings()
    engine = create_engine(settings.DB_DSN)
    TestingSessionLocal = sessionmaker(bind=engine)
    DeclarativeBase.metadata.create_all(bind=engine)
    return TestingSessionLocal()


@pytest.fixture()
def room_path(client_auth: TestClient, dbsession: Session):
    RESOURCE = "/timetable/room/"
    request_obj = {
        "name": datetime.now().isoformat(),
        "direction": "North",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.status_code == status.HTTP_200_OK, response.json()
    id_ = response.json()["id"]
    yield RESOURCE + str(id_)
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
    assert response.status_code == status.HTTP_200_OK, response.json()
    id_ = response.json()["id"]
    yield RESOURCE + str(id_)
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
    assert response.status_code == status.HTTP_200_OK, response.json()
    id_ = response.json()["id"]
    yield RESOURCE + str(id_)
    response_model: Lecturer = dbsession.query(Lecturer).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def photo_path(client_auth: TestClient, dbsession: Session, lecturer_path: str):
    RESOURCE = f"{lecturer_path}/photo"
    with open(os.path.dirname(__file__) + "/photo.png", "rb") as f:
        response = client_auth.post(RESOURCE, files={"photo": f})
    assert response.status_code == status.HTTP_200_OK, response.json()
    id_ = response.json()["id"]
    client_auth.post(f"{RESOURCE}/{id_}/review/", json={"action": "Approved"})
    yield RESOURCE + "/" + str(id_)
    response_model: CommentLecturer = dbsession.query(Photo).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()




@pytest.fixture()
def event_path(client_auth: TestClient, dbsession: Session, lecturer_path, room_path, group_path):
    RESOURCE = f"/timetable/event/"
    room_id = int(room_path.split("/")[-1])
    group_id = int(group_path.split("/")[-1])
    lecturer_id = int(lecturer_path.split("/")[-1])
    request_obj = {
        "name": "string",
        "room_id": [room_id],
        "group_id": group_id,
        "lecturer_id": [lecturer_id],
        "start_ts": "2022-08-26T22:32:38.575Z",
        "end_ts": "2022-08-26T22:32:38.575Z",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    id_ = response.json()["id"]
    yield RESOURCE + str(id_)
    response_model = dbsession.query(Event).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def room_factory(dbsession: Session):
    ids_ = []

    def _room_factory(client_auth: TestClient):
        RESOURCE = "/timetable/room/"
        request_obj = {
            "name": datetime.now().isoformat(),
            "direction": "North",
        }
        response = client_auth.post(RESOURCE, json=request_obj)
        assert response.status_code == status.HTTP_200_OK, response.json()
        nonlocal ids_
        ids_.append(yielding := response.json()["id"])
        return RESOURCE + str(yielding)

    yield _room_factory
    for id in ids_:
        response_model: Room = dbsession.query(Room).get(id)
        dbsession.delete(response_model)
        dbsession.commit()


@pytest.fixture()
def lecturer_factory(dbsession: Session):
    ids_ = []

    def _lecturer_factory(client_auth: TestClient):
        RESOURCE = "/timetable/lecturer/"
        request_obj = {
            "first_name": "Петр",
            "middle_name": "Васильевич",
            "last_name": "Тритий",
            "description": "Очень умный",
        }
        response = client_auth.post(RESOURCE, json=request_obj)
        assert response.status_code == status.HTTP_200_OK, response.json()
        nonlocal ids_
        ids_.append(yielding := response.json()["id"])
        return RESOURCE + str(yielding)

    yield _lecturer_factory
    for id in ids_:
        response_model: Lecturer = dbsession.query(Lecturer).get(id)
        dbsession.delete(response_model)
        dbsession.commit()


@pytest.fixture()
def group_factory(dbsession: Session):
    ids_ = []

    def _group_factory(client_auth: TestClient):
        RESOURCE = "/timetable/group/"
        request_obj = {
            "name": "",
            "number": datetime.now().isoformat(),
        }
        response = client_auth.post(RESOURCE, json=request_obj)
        assert response.status_code == status.HTTP_200_OK, response.json()
        nonlocal ids_
        ids_.append(yielding := response.json()["id"])
        return RESOURCE + str(yielding)

    yield _group_factory
    for id in ids_:
        response_model: Group = dbsession.query(Group).get(id)
        dbsession.delete(response_model)
        dbsession.commit()
