import os

from fastapi.testclient import TestClient
import pytest
from starlette import status
from calendar_backend.models.db import Photo
from sqlalchemy.orm import Session

from calendar_backend.settings import get_settings


settings = get_settings()
settings.STATIC_PATH = './static'


@pytest.fixture()
def photo_path(client_auth: TestClient, dbsession: Session, lecturer_path: str):
    RESOURCE = f"{lecturer_path}/photo"
    with open(os.path.dirname(__file__) + "/photo.png", "rb") as f:
        response = client_auth.post(RESOURCE, files={"photo": f})
    assert response.status_code == status.HTTP_200_OK, response.json()
    id_ = response.json()["id"]
    client_auth.post(f"/lecturer/photo/review/{id_}", json={"action": "Approved"})
    yield RESOURCE + "/" + str(id_)
    response_model = dbsession.query(Photo).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


def test_read_all(client_auth: TestClient, photo_path: str):
    photo_lib_path = '/'.join(photo_path.split("/")[:-1])
    response = client_auth.get(photo_lib_path, params={"limit": 10})
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_obj = response.json()
    assert response_obj["limit"] == 10
    assert len(response_obj["items"]) <= 10


def test_delete(client_auth: TestClient, photo_path: str):
    response = client_auth.get(photo_path)
    assert response.status_code == status.HTTP_200_OK

    response = client_auth.delete(photo_path)
    assert response.status_code == status.HTTP_200_OK, response.json()

    response = client_auth.get(photo_path)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_unsupported_format(lecturer_path: str, client_auth: TestClient):
    RESOURCE = f"{lecturer_path}/photo"
    with open(os.path.dirname(__file__) + "/photo.notpng", "rb") as f:
        response = client_auth.post(RESOURCE, files={"photo": f})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_corrupted_file(lecturer_path: str, client_auth: TestClient):
    RESOURCE = f"{lecturer_path}/photo"
    with open(os.path.dirname(__file__) + "/broken_photo.png", "rb") as f:
        response = client_auth.post(RESOURCE, files={"photo": f})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
