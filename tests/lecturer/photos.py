from fastapi.testclient import TestClient
from starlette import status
from calendar_backend.settings import get_settings


settings = get_settings()
settings.STATIC_PATH = './static'


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
