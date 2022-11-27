from fastapi.testclient import TestClient
import datetime
from sqlalchemy.orm import Session
from starlette import status

from calendar_backend.models import Event, Room, Lecturer, Group

RESOURCE = "/timetable/event/"


def test_create(client_auth: TestClient, dbsession: Session, room_path, group_path, lecturer_path):
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
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["room"][0]["id"] == room_id
    assert response_obj["group"]["id"] == request_obj["group_id"]
    assert response_obj["lecturer"][0]["id"] == lecturer_id
    assert response_obj["start_ts"][:20] == request_obj["start_ts"][:20]
    assert response_obj["end_ts"][:20] == request_obj["end_ts"][:20]
    response_model: Event = dbsession.query(Event).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert [row.id for row in response_model.room] == request_obj["room_id"]
    assert [row.id for row in response_model.lecturer] == request_obj["lecturer_id"]
    assert response_model.group_id == request_obj["group_id"]


def test_create_many(client_auth: TestClient, dbsession: Session, room_factory, group_factory, lecturer_factory):
    room_path1 = room_factory(client_auth)
    group_path1 = group_factory(client_auth)
    lecturer_path1 = lecturer_factory(client_auth)
    room_path2 = room_factory(client_auth)
    group_path2 = group_factory(client_auth)
    lecturer_path2 = lecturer_factory(client_auth)
    room_id1 = int(room_path1.split("/")[-1])
    group_id1 = int(group_path1.split("/")[-1])
    lecturer_id1 = int(lecturer_path1.split("/")[-1])
    room_id2 = int(room_path2.split("/")[-1])
    group_id2 = int(group_path2.split("/")[-1])
    lecturer_id2 = int(lecturer_path2.split("/")[-1])
    request_obj = [
        {
            "name": "string",
            "room_id": [room_id1],
            "group_id": group_id1,
            "lecturer_id": [lecturer_id1],
            "start_ts": "2022-08-26T22:32:38.575Z",
            "end_ts": "2022-08-26T22:32:38.575Z",
        },
        {
            "name": "string",
            "room_id": [room_id2],
            "group_id": group_id2,
            "lecturer_id": [lecturer_id2],
            "start_ts": "2022-08-26T22:32:38.575Z",
            "end_ts": "2022-08-26T22:32:38.575Z",
        },
    ]
    response = client_auth.post(f"{RESOURCE}bulk", json=request_obj)
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_obj = response.json()
    assert response_obj[0]["name"] == request_obj[0]["name"]
    assert response_obj[0]["room"][0]["id"] == room_id1
    assert response_obj[0]["group"]["id"] == request_obj[0]["group_id"]
    assert response_obj[0]["lecturer"][0]["id"] == lecturer_id1
    assert response_obj[0]["start_ts"][:20] == request_obj[0]["start_ts"][:20]
    assert response_obj[0]["end_ts"][:20] == request_obj[0]["end_ts"][:20]
    response_model: Event = dbsession.query(Event).get(response_obj[0]["id"])
    assert response_model.name == request_obj[0]["name"]
    assert [row.id for row in response_model.room] == request_obj[0]["room_id"]
    assert [row.id for row in response_model.lecturer] == request_obj[0]["lecturer_id"]
    assert response_model.group_id == request_obj[0]["group_id"]

    assert response_obj[1]["name"] == request_obj[1]["name"]
    assert response_obj[1]["room"][0]["id"] == room_id2
    assert response_obj[1]["group"]["id"] == request_obj[1]["group_id"]
    assert response_obj[1]["lecturer"][0]["id"] == lecturer_id2
    assert response_obj[1]["start_ts"][:20] == request_obj[1]["start_ts"][:20]
    assert response_obj[1]["end_ts"][:20] == request_obj[1]["end_ts"][:20]
    response_model: Event = dbsession.query(Event).get(response_obj[1]["id"])
    assert response_model.name == request_obj[1]["name"]
    assert [row.id for row in response_model.room] == request_obj[1]["room_id"]
    assert [row.id for row in response_model.lecturer] == request_obj[1]["lecturer_id"]
    assert response_model.group_id == request_obj[1]["group_id"]


def test_delete(client_auth: TestClient, dbsession: Session, room_path, lecturer_path, group_path):
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
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["room"][0]["id"] == request_obj["room_id"][0]
    assert response_obj["group"]["id"] == request_obj["group_id"]
    assert response_obj["lecturer"][0]["id"] == request_obj["lecturer_id"][0]
    assert response_obj["start_ts"][:20] == request_obj["start_ts"][:20]
    assert response_obj["end_ts"][:20] == request_obj["end_ts"][:20]
    id_ = response_obj['id']

    # Delete
    response = client_auth.delete(RESOURCE + f"{id_}")
    assert response.status_code == status.HTTP_200_OK, response.json()

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()

    # Read all
    response = client_auth.get(
        RESOURCE,
        params={
            "group_id": group_id,
            "start": "2022-08-26",
            "end": "2022-08-27",
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    for item in response.json()["items"]:
        assert item["id"] != id_

    # Ok db
    response_model: Event = dbsession.query(Event).get(response_obj["id"])
    assert response_model.is_deleted

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_update_all(client_auth: TestClient, dbsession: Session):
    # Create
    room = Room(name="5-07" + datetime.datetime.utcnow().isoformat(), direction="North")
    lecturer = Lecturer(first_name="s", middle_name="s", last_name="s")
    group = Group(name="", number="202" + datetime.datetime.utcnow().isoformat())
    dbsession.add(room)
    dbsession.add(lecturer)
    dbsession.add(group)
    dbsession.commit()
    request_obj = {
        "name": "string",
        "room_id": [room.id],
        "group_id": group.id,
        "lecturer_id": [lecturer.id],
        "start_ts": "2022-08-26T22:32:38.575Z",
        "end_ts": "2022-08-26T22:32:38.575Z",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["room"][0]["id"] == request_obj["room_id"][0]
    assert response_obj["group"]["id"] == request_obj["group_id"]
    assert response_obj["lecturer"][0]["id"] == request_obj["lecturer_id"][0]
    assert response_obj["start_ts"][:20] == request_obj["start_ts"][:20]
    assert response_obj["end_ts"][:20] == request_obj["end_ts"][:20]
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["room"][0]["id"] == request_obj["room_id"][0]
    assert response_obj["group"]["id"] == request_obj["group_id"]
    assert response_obj["lecturer"][0]["id"] == request_obj["lecturer_id"][0]
    assert response_obj["start_ts"][:20] == request_obj["start_ts"][:20]
    assert response_obj["end_ts"][:20] == request_obj["end_ts"][:20]

    # Update
    request_obj_2 = {
        "name": "frfrf",
        "room_id": [room.id],
        "group_id": group.id,
        "lecturer_id": [lecturer.id],
        "start_ts": "2022-08-26T22:32:38.575Z",
        "end_ts": "2022-08-26T22:32:38.575Z",
    }
    client_auth.patch(RESOURCE + f"{id_}", json=request_obj_2)
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj_2["name"]
    assert response_obj["room"][0]["id"] == request_obj_2["room_id"][0]
    assert response_obj["group"]["id"] == request_obj_2["group_id"]
    assert response_obj["lecturer"][0]["id"] == request_obj_2["lecturer_id"][0]
    assert response_obj["start_ts"][:20] == request_obj_2["start_ts"][:20]
    assert response_obj["end_ts"][:20] == request_obj_2["end_ts"][:20]

    # Read all
    response = client_auth.get(RESOURCE, params={"group_id": group.id, "detail": ""})
    assert response.status_code == status.HTTP_200_OK, response.json()
    for item in response.json()["items"]:
        if item["id"] == id_:
            assert item[0]["name"] == request_obj["name"]
            assert item[0]["room"][0]["id"] == request_obj["room_id"][0]
            assert item[0]["group"]["id"] == request_obj["group_id"]
            assert item[0]["lecturer"][0]["id"] == request_obj["lecturer_id"][0]
            assert item["start_ts"][:20] == request_obj_2["start_ts"][:20]
            assert item["end_ts"][:20] == request_obj_2["end_ts"][:20]

    # Ok db
    response_model: Event = dbsession.query(Event).get(response_obj["id"])
    assert response_model.name == request_obj_2["name"]
    assert [row.id for row in response_model.room] == request_obj_2["room_id"]
    assert [row.id for row in response_model.lecturer] == request_obj_2["lecturer_id"]
    assert response_model.group_id == request_obj_2["group_id"]
    assert str(response_model.start_ts.isoformat())[:20] == request_obj_2["start_ts"][:20]
    assert str(response_model.end_ts.isoformat())[:20] == request_obj_2["end_ts"][:20]

    # Clear db
    dbsession.delete(response_model)
    dbsession.delete(room)
    dbsession.delete(lecturer)
    dbsession.delete(group)
    dbsession.commit()


def test_delete_from_to(client_auth: TestClient, dbsession: Session, room_factory, group_factory, lecturer_factory):
    room_path1 = room_factory(client_auth)
    group_path1 = group_factory(client_auth)
    lecturer_path1 = lecturer_factory(client_auth)
    room_path2 = room_factory(client_auth)
    group_path2 = group_factory(client_auth)
    lecturer_path2 = lecturer_factory(client_auth)
    room_id1 = int(room_path1.split("/")[-1])
    group_id1 = int(group_path1.split("/")[-1])
    lecturer_id1 = int(lecturer_path1.split("/")[-1])
    room_id2 = int(room_path2.split("/")[-1])
    group_id2 = int(group_path2.split("/")[-1])
    lecturer_id2 = int(lecturer_path2.split("/")[-1])
    request_obj = [
        {
            "name": "string",
            "room_id": [room_id1],
            "group_id": group_id1,
            "lecturer_id": [lecturer_id1],
            "start_ts": "2022-08-26T22:32:38.575Z",
            "end_ts": "2022-08-26T22:32:38.575Z",
        },
        {
            "name": "string",
            "room_id": [room_id2],
            "group_id": group_id2,
            "lecturer_id": [lecturer_id2],
            "start_ts": "2022-08-26T22:32:38.575Z",
            "end_ts": "2022-08-26T22:32:38.575Z",
        },
    ]
    response = client_auth.post(f"{RESOURCE}bulk", json=request_obj)
    created = response.json()
    assert response.status_code == status.HTTP_200_OK, response.json()
    response = client_auth.delete(f"{RESOURCE}bulk", data={"start": "2022-08-26", "end": "2022-08-27"})
    assert response.status_code == 200
    response = client_auth.get(f"{RESOURCE}{created[0]['id']}")
    assert response.status_code == 404
    response = client_auth.get(f"{RESOURCE}{created[1]['id']}")
    assert response.status_code == 404
    obj1 = dbsession.query(Event).filter(Event.id == created[0]["id"]).one()
    obj2 = dbsession.query(Event).filter(Event.id == created[1]["id"]).one()
    for row in (obj1, obj2):
        dbsession.delete(row)
