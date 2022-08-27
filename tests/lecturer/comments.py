from fastapi.testclient import TestClient


def test_read_all(client_auth: TestClient, comment_path: str):
    comment_lib_path = '/'.join(comment_path.split("/")[:-1])
    response = client_auth.get(comment_lib_path, params={"limit": 10})
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["limit"] == 10
    assert len(response_obj["items"]) <= 10


def test_delete(client_auth: TestClient, comment_path: str):
    response = client_auth.delete(comment_path)
    assert response.ok, response.json()


def test_patch(client_auth: TestClient, comment_path: str):
    request = {
        "text": "Не очень умный коммент",
    }
    response = client_auth.patch(comment_path, json=request)
    assert response.ok, response.json()
    assert response.json()["text"] == request["text"]
