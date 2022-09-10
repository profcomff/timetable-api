import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from calendar_backend.exceptions import ForbiddenAction
from calendar_backend.models import CommentEvent


@pytest.fixture()
def comment_event_path(client_auth: TestClient, dbsession: Session, event_path: str):
    RESOURCE = f"{event_path}/comment/"
    request_obj = {
        "author_name": "Аноним",
        "text": "Очень умный коммент",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    id_ = response.json()["id"]
    client_auth.post(f"{RESOURCE}{id_}/review/", params={"action": "Approved"})
    yield RESOURCE + str(id_)
    response_model: CommentEvent = dbsession.query(CommentEvent).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def comment_event_path_no_review(client_auth: TestClient, dbsession: Session, event_path: str):
    RESOURCE = f"{event_path}/comment/"
    request_obj = {
        "author_name": "Аноним",
        "text": "Очень умный коммент",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    id_ = response.json()["id"]
    yield RESOURCE + str(id_)
    response_model: CommentEvent = dbsession.query(CommentEvent).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def comment_event_path_declined_review(client_auth: TestClient, dbsession: Session, event_path: str):
    RESOURCE = f"{event_path}/comment/"
    request_obj = {
        "author_name": "Аноним",
        "text": "Очень умный коммент",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    id_ = response.json()["id"]
    client_auth.post(f"{RESOURCE}{id_}/review/", params={"action": "Declined"})
    yield RESOURCE + str(id_)
    response_model: CommentEvent = dbsession.query(CommentEvent).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def comment_event_path_for_read_all(client_auth: TestClient, dbsession: Session, event_path: str):
    RESOURCE = f"{event_path}/comment/"
    request_obj = {
        "author_name": "Аноним",
        "text": "Очень умный коммент",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    id_ = response.json()["id"]
    client_auth.post(f"{RESOURCE}{id_}/review/", params={"action": "Approved"})
    yield RESOURCE
    response_model: CommentEvent = dbsession.query(CommentEvent).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


def test_read_all(client_auth: TestClient, comment_event_path_for_read_all: str):
    response = client_auth.get(comment_event_path_for_read_all, params={"limit": 10})
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["limit"] == 10
    assert len(response_obj["items"]) <= 10


def test_delete(client_auth: TestClient, comment_event_path: str):
    response = client_auth.delete(comment_event_path)
    assert response.ok, response.json()


def test_patch(client_auth: TestClient, comment_event_path: str, comment_event_path_no_review: str):
    request = {
        "text": "Не очень умный коммент",
    }
    response = client_auth.patch(comment_event_path, json=request)
    assert response.status_code == 403

    response = client_auth.patch(comment_event_path_no_review, json=request)
    assert response.ok, response.json()
    assert response.json()["text"] == request["text"]


def test_review(client_auth: TestClient, comment_event_path_declined_review):
    response = client_auth.get(comment_event_path_declined_review)
    assert response.status_code == 404
