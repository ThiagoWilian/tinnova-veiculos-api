from fastapi.testclient import TestClient


def test_login_returns_bearer_token(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "admin123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_invalid_credentials_returns_401(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "errado"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"
