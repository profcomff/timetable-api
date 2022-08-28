from fastapi.testclient import TestClient


def test_read_all(client_auth: TestClient, comment_path: str):
    response = client_auth.get(comment_path, params={"limit": 10})
    assert response.ok, response.json()
    response_obj = response.json()
    assert response_obj["limit"] == 10
    assert len(response_obj["comments"]) <= 10


def test_delete(client_auth: TestClient, comment_path_for_delete_and_patch: str):
    response = client_auth.delete(comment_path_for_delete_and_patch)
    assert response.ok, response.json()


def test_patch(client_auth: TestClient, comment_path_for_delete_and_patch: str):
    request = {
        "text": "Не очень умный коммент",
    }
    response = client_auth.patch(comment_path_for_delete_and_patch, json=request)
    assert response.ok, response.json()
    assert response.json()["text"] == request["text"]
