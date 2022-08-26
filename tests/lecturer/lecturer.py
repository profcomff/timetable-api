from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from calendar_backend.models import Group
from calendar_backend.models.db import Lecturer


RESOURCE = "/timetable/lecturer/"


def test_create(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "first_name": "Петр",
        "middle_name": "Васильевич",
        "last_name": "Тритий",
        "description": "Очень умный",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    id_ = response_obj.pop("id")
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj

    # Ok db
    response_model: Lecturer = dbsession.query(Lecturer).get(id_)
    assert {
        "first_name": response_model.first_name,
        "middle_name": response_model.middle_name,
        "last_name": response_model.last_name,
        "description": response_model.description,
    } == request_obj

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_read(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "first_name": "Петр",
        "middle_name": "Васильевич",
        "last_name": "Тритий",
        "description": "Очень умный",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()
    response_obj: dict = response.json()
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj
    assert {
        "id",
        "first_name",
        "middle_name",
        "last_name",
        "avatar_id",
        "avatar_link",
        "description",
        "comments",
        "events",
    } == set(response_obj.keys())

    # Ok db
    response_model: Lecturer = dbsession.query(Lecturer).get(id_)
    assert {
        "first_name": response_model.first_name,
        "middle_name": response_model.middle_name,
        "last_name": response_model.last_name,
        "description": response_model.description,
    } == request_obj

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_delete(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "first_name": "Петр",
        "middle_name": "Васильевич",
        "last_name": "Тритий",
        "description": "Очень умный",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()
    response_obj: dict = response.json()
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj
    assert {
        "id",
        "first_name",
        "middle_name",
        "last_name",
        "avatar_id",
        "avatar_link",
        "description",
        "comments",
        "events",
    } == set(response_obj.keys())

    # Delete
    response = client_auth.delete(RESOURCE + f"{id_}/")

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.status_code == 404, response.json()

    # Read all
    response = client_auth.get(RESOURCE, params={"limit": 0}, json=request_obj)
    assert response.ok
    for item in response.json()["items"]:
        assert item["id"] != id_

    # Ok db
    response_model: Lecturer = dbsession.query(Lecturer).get(id_)
    assert {
        "first_name": response_model.first_name,
        "middle_name": response_model.middle_name,
        "last_name": response_model.last_name,
        "description": response_model.description,
    } == request_obj
    assert response_model.is_deleted

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_update_name(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "first_name": "Петр",
        "middle_name": "Васильевич",
        "last_name": "Тритий",
        "description": "Очень умный",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj

    # Update
    request_obj_2 = {
        "first_name": "Hello",
    }
    request_obj.update(request_obj_2)
    response = client_auth.patch(RESOURCE + f"{id_}/", json=request_obj_2)
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj

    # Read all
    response = client_auth.get(RESOURCE, params={"limit": 0}, json=request_obj)
    assert response.ok
    for item in response.json()["items"]:
        if item["id"] == id_:
            assert {
                "first_name": item["first_name"],
                "middle_name": item["middle_name"],
                "last_name": item["last_name"],
                "description": item["description"],
            } == request_obj

    # Ok db
    response_model: Lecturer = dbsession.query(Lecturer).get(id_)
    assert {
        "first_name": response_model.first_name,
        "middle_name": response_model.middle_name,
        "last_name": response_model.last_name,
        "description": response_model.description,
    } == request_obj

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()


def test_update_all(client_auth: TestClient, dbsession: Session):
    # Create
    request_obj = {
        "first_name": "Петр",
        "middle_name": "Васильевич",
        "last_name": "Тритий",
        "description": "Очень умный",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.ok, response.json()
    response_obj = response.json()
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj
    id_ = response_obj['id']

    # Read
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj

    # Update
    request_obj_2 = {
        "first_name": "Петр",
        "middle_name": "Шушакович",
        "last_name": "Семенов",
        "description": "Третья попытка",
    }
    request_obj.update(request_obj_2)
    client_auth.patch(RESOURCE + f"{id_}/", json=request_obj_2)
    response = client_auth.get(RESOURCE + f"{id_}/")
    assert response.ok, response.json()
    response_obj = response.json()
    assert {
        "first_name": response_obj["first_name"],
        "middle_name": response_obj["middle_name"],
        "last_name": response_obj["last_name"],
        "description": response_obj["description"],
    } == request_obj

    # Read all
    response = client_auth.get(RESOURCE, params={"limit": 0}, json=request_obj)
    assert response.ok
    for item in response.json()["items"]:
        if item["id"] == id_:
            assert {
                "first_name": item["first_name"],
                "middle_name": item["middle_name"],
                "last_name": item["last_name"],
                "description": item["description"],
            } == request_obj

    # Ok db
    response_model: Lecturer = dbsession.query(Lecturer).get(id_)
    assert {
        "first_name": response_model.first_name,
        "middle_name": response_model.middle_name,
        "last_name": response_model.last_name,
        "description": response_model.description,
    } == request_obj.update(request_obj_2)

    # Clear db
    dbsession.delete(response_model)
    dbsession.commit()
