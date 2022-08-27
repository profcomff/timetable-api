from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from calendar_backend.models import Group


RESOURCE = "/timetable/group/"


def test_create(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "name": "",
        "number": "test102" + datetime.utcnow().isoformat()
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]

    # Ok db
    response_model: Group = dbsession.query(Group).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert response_model.number == request_obj["number"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_read(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "name": "",
        "number": "test103" + datetime.utcnow().isoformat()
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE+f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]

    # Ok db
    response_model: Group = dbsession.query(Group).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert response_model.number == request_obj["number"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_delete(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "name": "",
        "number": "test104" + datetime.utcnow().isoformat()
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE+f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]

    # Delete
    response = client_auth.delete(RESOURCE+f"{id_}/")

    # Read
    response = client_auth.get(RESOURCE+f"{id_}/")
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
    assert response_obj["number"] == request_obj["number"]

    # Ok db
    response_model: Group = dbsession.query(Group).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert response_model.number == request_obj["number"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_update_name(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "name": "",
        "number": "test104" + datetime.utcnow().isoformat()
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE+f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]

    # Update
    request_obj_2 = {
        "name": "Hello",
    }
    response = client_auth.patch(RESOURCE+f"{id_}/", json=request_obj_2)
    response = client_auth.get(RESOURCE+f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj_2["name"]
    assert response_obj["number"] == request_obj["number"]

    # Read all
    response = client_auth.get(RESOURCE, params={"limit": 0}, json=request_obj)
    assert response.ok
    for item in response.json()["items"]:
        if item["id"] == id_:
            assert item["name"] == request_obj_2["name"]
            assert item["number"] == request_obj["number"]

    # Ok reverse
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]

    # Ok db
    response_model: Group = dbsession.query(Group).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert response_model.number == request_obj["number"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_update_all(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "name": "",
        "number": "test104" + datetime.utcnow().isoformat()
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE+f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]

    # Update
    request_obj_2 = {
        "name": "HelloWorld",
        "number": "test105" + datetime.utcnow().isoformat()
    }
    client_auth.patch(RESOURCE+f"{id_}/", json=request_obj_2)
    response = client_auth.get(RESOURCE+f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj_2["name"]
    assert response_obj["number"] == request_obj_2["number"]

    # Read all
    response = client_auth.get(RESOURCE, params={"limit": 0}, json=request_obj)
    assert response.ok
    for item in response.json()["items"]:
        if item["id"] == id_:
            assert item["name"] == request_obj_2["name"]
            assert item["number"] == request_obj_2["number"]

    # Ok reverse
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["name"] == request_obj["name"]
    assert response_obj["number"] == request_obj["number"]

    # Ok db
    response_model: Group = dbsession.query(Group).get(response_obj["id"])
    assert response_model.name == request_obj["name"]
    assert response_model.number == request_obj["number"]

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()
