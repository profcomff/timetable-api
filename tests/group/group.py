from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from calendar_backend.models import Group


RESOURCE = "/timetable/group/"


def test_create(client_auth: TestClient, dbsession: Session):
    request_obj = {
        "name": "",
        "number": "test204"
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]
    response_model: Group = dbsession.query(Group).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert response_model.number == request_obj["number"]


def test_read():
    pass


def test_delete():
    pass


def test_update():
    pass
