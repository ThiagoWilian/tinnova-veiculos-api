from fastapi.testclient import TestClient


def test_get_veiculos_requires_token(client: TestClient) -> None:
    response = client.get("/veiculos")

    assert response.status_code == 401


def test_user_can_access_gets(
    client: TestClient,
    user_headers: dict[str, str],
    ) -> None:
    response = client.get("/veiculos", headers=user_headers)

    assert response.status_code == 200


def test_user_cannot_create_vehicle(
    client: TestClient,
    user_headers: dict[str, str],
    veiculo_payload: dict[str, object],
    ) -> None:
    response = client.post("/veiculos", json=veiculo_payload, headers=user_headers)

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "FORBIDDEN"
