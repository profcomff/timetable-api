from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from calendar_backend.models import Room

RESOURCE = "/timetable/room/"


def test_create(client_auth: TestClient, dbsession: Session):
    request_obj = {
        "name": "5-02",
        "direction": "North"
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["direction"] == request_obj["direction"]
    response_model: Room = dbsession.query(Room).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert response_model.direction == request_obj["direction"]


def test_read():
    pass


def test_delete():
    pass


def test_update():
    pass