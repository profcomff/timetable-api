from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from calendar_backend.models import Lesson, Room, Lecturer, Group

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


def test_read(client_auth: TestClient, dbsession: Session):
    # Create
    room = Room(name="5-07", direction="North")
    lecturer = Lecturer(first_name="s", middle_name="s", last_name="s")
    group = Group(name="", number="202")
    dbsession.add([room, lecturer, group])
    dbsession.commit()
    request_obj = {
          "name": "string",
          "room_id": [
            room.id
          ],
          "group_id": group.id,
          "lecturer_id": [
            lecturer.id
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
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["room_id"] == request_obj["room_id"]
    assert response_obj["group_id"] == request_obj["group_id"]
    assert response_obj["lecturer_id"] == request_obj["lecturer_id"]
    assert response_obj["start_ts"] == request_obj["start_ts"]
    assert response_obj["end_ts"] == request_obj["end_ts"]

    # Ok db
    response_model: Group = dbsession.query(Group).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert [row.id for row in response_model.room] == request_obj["room_id"]
    assert [row.id for row in response_model.lecturer] == request_obj["lecturer_id"]
    assert response_model.group_id == request_obj["group_id"]
    assert response_model.start_ts == request_obj["start_ts"]
    assert response_model.end_ts == request_obj["end_ts"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_delete(client_auth: TestClient, dbsession: Session):
    # Create
    room = Room(name="5-07", direction="North")
    lecturer = Lecturer(first_name="s", middle_name="s", last_name="s")
    group = Group(name="", number="202")
    dbsession.add([room, lecturer, group])
    dbsession.commit()
    request_obj = {
        "name": "string",
        "room_id": [
            room.id
        ],
        "group_id": group.id,
        "lecturer_id": [
            lecturer.id
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
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["room_id"] == request_obj["room_id"]
    assert response_obj["group_id"] == request_obj["group_id"]
    assert response_obj["lecturer_id"] == request_obj["lecturer_id"]
    assert response_obj["start_ts"] == request_obj["start_ts"]
    assert response_obj["end_ts"] == request_obj["end_ts"]


    # Delete
    response = client_auth.delete(RESOURCE + f"{id_}/")

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()

    # Read all
    response = client_auth.get(RESOURCE, params={"limit": 0}, json=request_obj)
    assert response.ok
    for item in response.json()["items"]:
        assert item["id"] != id_

    # Ok reverse
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["room_id"] == request_obj["room_id"]
    assert response_obj["group_id"] == request_obj["group_id"]
    assert response_obj["lecturer_id"] == request_obj["lecturer_id"]
    assert response_obj["start_ts"] == request_obj["start_ts"]
    assert response_obj["end_ts"] == request_obj["end_ts"]

    # Ok db
    response_model: Lesson = dbsession.query(Lesson).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert [row.id for row in response_model.room] == request_obj["room_id"]
    assert [row.id for row in response_model.lecturer] == request_obj["lecturer_id"]
    assert response_model.group_id == request_obj["group_id"]
    assert response_model.start_ts == request_obj["start_ts"]
    assert response_model.end_ts == request_obj["end_ts"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_update_all(client_auth: TestClient, dbsession: Session):
    # Create
    room = Room(name="5-07", direction="North")
    lecturer = Lecturer(first_name="s", middle_name="s", last_name="s")
    group = Group(name="", number="202")
    dbsession.add([room, lecturer, group])
    dbsession.commit()
    request_obj = {
        "name": "string",
        "room_id": [
            room.id
        ],
        "group_id": group.id,
        "lecturer_id": [
            lecturer.id
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
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE+f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["room_id"] == request_obj["room_id"]
    assert response_obj["group_id"] == request_obj["group_id"]
    assert response_obj["lecturer_id"] == request_obj["lecturer_id"]
    assert response_obj["start_ts"] == request_obj["start_ts"]
    assert response_obj["end_ts"] == request_obj["end_ts"]

    # Update
    request_obj_2 = {
        "name": "frfrf",
        "room_id": [
            room.id
        ],
        "group_id": group.id,
        "lecturer_id": [
            lecturer.id
        ],
        "start_ts": "2022-08-26T22:32:38.575Z",
        "end_ts": "2022-08-26T22:32:38.575Z"
    }
    client_auth.patch(RESOURCE+f"{id_}/", json=request_obj_2)
    response = client_auth.get(RESOURCE+f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj_2["name"]
    assert response_obj["room_id"] == request_obj_2["room_id"]
    assert response_obj["group_id"] == request_obj_2["group_id"]
    assert response_obj["lecturer_id"] == request_obj_2["lecturer_id"]
    assert response_obj["start_ts"] == request_obj_2["start_ts"]
    assert response_obj["end_ts"] == request_obj_2["end_ts"]

    # Read all
    response = client_auth.get(RESOURCE, params={"limit": 0}, json=request_obj)
    assert response.ok
    for item in response.json()["items"]:
        if item["id"] == id_:
            assert item["name"] == request_obj_2["name"]
            assert item["room_id"] == request_obj_2["room_id"]
            assert item["group_id"] == request_obj_2["group_id"]
            assert item["lecturer_id"] == request_obj_2["lecturer_id"]
            assert item["start_ts"] == request_obj_2["start_ts"]
            assert item["end_ts"] == request_obj_2["end_ts"]

    # Ok reverse
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["room_id"] == request_obj["room_id"]
    assert response_obj["group_id"] == request_obj["group_id"]
    assert response_obj["lecturer_id"] == request_obj["lecturer_id"]
    assert response_obj["start_ts"] == request_obj["start_ts"]
    assert response_obj["end_ts"] == request_obj["end_ts"]

    # Ok db
    response_model: Lesson = dbsession.query(Lesson).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert [row.id for row in response_model.room] == request_obj["room_id"]
    assert [row.id for row in response_model.lecturer] == request_obj["lecturer_id"]
    assert response_model.group_id == request_obj["group_id"]
    assert response_model.start_ts == request_obj["start_ts"]
    assert response_model.end_ts == request_obj["end_ts"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()