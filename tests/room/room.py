import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from calendar_backend.models import Room

RESOURCE = "/timetable/room/"


def test_create(client_auth: TestClient, dbsession: Session):
    request_obj = {
        "name": "5-02" + datetime.datetime.utcnow().isoformat(),
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


def test_read(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "name": "5-02" + datetime.datetime.utcnow().isoformat(),
        "direction": "North"
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["direction"] == request_obj["direction"]
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["direction"] == request_obj["direction"]

    # Ok db
    response_model: Room = dbsession.query(Room).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert response_model.direction == request_obj["direction"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_delete(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "name": "5-02" + datetime.datetime.utcnow().isoformat(),
        "direction": "North"
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["direction"] == request_obj["direction"]
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["direction"] == request_obj["direction"]

    # Delete
    response = client_auth.delete(RESOURCE + f"{id_}/")

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()

    # Read all
    response = client_auth.get(RESOURCE, params={"limit": 0})
    assert response.ok
    for item in response.json()["items"]:
        assert item["id"] != id_

    # Ok db
    response_model: Room = dbsession.query(Room).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert response_model.direction == request_obj["direction"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_update_all(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "name": "" + datetime.datetime.utcnow().isoformat(),
        "direction": "North"
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["direction"] == request_obj["direction"]
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE+f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["direction"] == request_obj["direction"]

    # Update
    request_obj_2 = {
        "name": "" + datetime.datetime.utcnow().isoformat(),
        "direction": "North"
    }
    client_auth.patch(RESOURCE+f"{id_}", json=request_obj_2)
    response = client_auth.get(RESOURCE+f"{id_}")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj_2["name"]
    assert response_obj["direction"] == request_obj_2["direction"]

    # Read all
    response = client_auth.get(RESOURCE, params={"limit": 0}, json=request_obj)
    assert response.ok
    for item in response.json()["items"]:
        if item["id"] == id_:
            assert item["name"] == request_obj_2["name"]
            assert item["direction"] == request_obj_2["direction"]
            break

    # Ok db
    response_model: Room = dbsession.query(Room).get(response_obj["id"])
    assert response_model.name == request_obj_2["name"]
    assert response_model.direction == request_obj_2["direction"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()
