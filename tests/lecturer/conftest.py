import os.path
import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from calendar_backend.models.db import Lecturer, CommentsLecturer, Photo


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
