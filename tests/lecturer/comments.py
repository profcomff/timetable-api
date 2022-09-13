import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from calendar_backend.models import CommentLecturer


@pytest.fixture()
def comment_path_no_review(client_auth: TestClient, dbsession: Session, lecturer_path: str):
    RESOURCE = f"{lecturer_path}/comment/"
    request_obj = {
        "author_name": "Аноним",
        "text": "Очень умный коммент",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    id_ = response.json()["id"]
    yield RESOURCE + str(id_)
    response_model: CommentLecturer = dbsession.query(CommentLecturer).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def comment_path_for_read_all(client_auth: TestClient, dbsession: Session, lecturer_path: str):
    RESOURCE = f"{lecturer_path}/comment/"
    request_obj = {
        "author_name": "Аноним",
        "text": "Очень умный коммент",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    id_ = response.json()["id"]
    client_auth.post(f"{RESOURCE}{id_}/review/", params={"action": "Approved"})
    yield RESOURCE
    response_model: CommentLecturer = dbsession.query(CommentLecturer).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


def test_read_all(client_auth: TestClient, comment_path_for_read_all: str):
    response = client_auth.get(comment_path_for_read_all, params={"limit": 10})
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["limit"] == 10
    assert len(response_obj["items"]) <= 10


def test_delete(client_auth: TestClient, comment_path_no_review: str):
    client_auth.post(f"{comment_path_no_review}/review/", params={"action": "Approved"})
    response = client_auth.delete(comment_path_no_review)
    assert response.ok, response.json()


def test_patch(client_auth: TestClient, comment_path_no_review: str):
    request = {
        "text": "Не очень умный коммент",
    }

    response = client_auth.patch(comment_path_no_review, json=request)
    assert response.ok, response.json()
    assert response.json()["text"] == request["text"]

    client_auth.post(f"{comment_path_no_review}/review/", params={"action": "Approved"})

    response = client_auth.patch(comment_path_no_review, json=request)
    assert response.status_code == 403


def test_review(client_auth: TestClient, comment_path_no_review: str):
    client_auth.post(f"{comment_path_no_review}/review/", params={"action": "Declined"})
    response = client_auth.get(comment_path_no_review)
    assert response.status_code == 404
