from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from calendar_backend.models import Lesson

RESOURCE = "/timetable/event/"


def test_create(client_auth: TestClient, dbsession: Session):
    request_obj = {
          "name": "string",
          "room_id": [
            0
          ],
          "group_id": 0,
          "lecturer_id": [
            0
          ],
          "start_ts": "2022-08-26T22:32:38.575Z",
          "end_ts": "2022-08-26T22:32:38.575Z"
}
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["room_id"] == request_obj["room_id"]
    assert response_obj["group_id"] == request_obj["group_id"]
    assert response_obj["lecturer_id"] == request_obj["lecturer_id"]
    assert response_obj["start_ts"] == request_obj["start_ts"]
    assert response_obj["end_ts"] == request_obj["end_ts"]
    response_model: Lesson = dbsession.query(Lesson).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert [row.id for row in response_model.room] == request_obj["room_id"]
    assert [row.id for row in response_model.lecturer] == request_obj["lecturer_id"]
    assert response_model.group_id == request_obj["group_id"]
    assert response_model.start_ts == request_obj["start_ts"]
    assert response_model.end_ts == request_obj["end_ts"]


def test_read():
    pass


def test_delete():
    pass


def test_update():
    pass