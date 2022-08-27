from fastapi.testclient import TestClient


def test_read_all(client_auth: TestClient, photo_path: str):
    photo_lib_path = '/'.join(photo_path.split("/")[:-1])
    response = client_auth.get(photo_lib_path, params={"limit": 10})
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["limit"] == 10
    assert len(response_obj["items"]) <= 10


def test_delete(client_auth: TestClient, photo_path: str):
    response = client_auth.delete(photo_path)
    assert response.ok, response.json()
