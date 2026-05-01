from fastapi.testclient import TestClient


def test_admin_creates_vehicle(
    client: TestClient,
    admin_headers: dict[str, str],
    veiculo_payload: dict[str, object],
    ) -> None:
    response = client.post("/veiculos", json=veiculo_payload, headers=admin_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["placa"] == "ABC1D23"
    assert data["preco_usd"] == "20000.00"


def test_duplicate_plate_returns_409(
    client: TestClient,
    admin_headers: dict[str, str],
    veiculo_payload: dict[str, object],
    ) -> None:
    client.post("/veiculos", json=veiculo_payload, headers=admin_headers)
    response = client.post("/veiculos", json=veiculo_payload, headers=admin_headers)

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "VEHICLE_PLATE_CONFLICT"


def test_put_and_patch_vehicle(
    client: TestClient,
    admin_headers: dict[str, str],
    veiculo_payload: dict[str, object],
    ) -> None:
    created = client.post("/veiculos", json=veiculo_payload, headers=admin_headers).json()

    put_payload = {
        **veiculo_payload,
        "modelo": "Corolla XEI",
        "preco_brl": "125000.00",
    }
    put_response = client.put(f"/veiculos/{created['id']}", json=put_payload, headers=admin_headers)
    assert put_response.status_code == 200
    assert put_response.json()["modelo"] == "Corolla XEI"
    assert put_response.json()["preco_usd"] == "25000.00"

    patch_response = client.patch(
        f"/veiculos/{created['id']}",
        json={"cor": "Preto"},
        headers=admin_headers,
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["cor"] == "Preto"


def test_patch_empty_payload_returns_422(
    client: TestClient,
    admin_headers: dict[str, str],
    veiculo_payload: dict[str, object],
    ) -> None:
    created = client.post("/veiculos", json=veiculo_payload, headers=admin_headers).json()

    response = client.patch(f"/veiculos/{created['id']}", json={}, headers=admin_headers)

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "VALIDATION_ERROR"


def test_delete_soft_deletes_vehicle(
    client: TestClient,
    admin_headers: dict[str, str],
    veiculo_payload: dict[str, object],
    ) -> None:
    created = client.post("/veiculos", json=veiculo_payload, headers=admin_headers).json()

    delete_response = client.delete(f"/veiculos/{created['id']}", headers=admin_headers)
    detail_response = client.get(f"/veiculos/{created['id']}", headers=admin_headers)

    assert delete_response.status_code == 204
    assert detail_response.status_code == 404