from fastapi.testclient import TestClient


def test_admin_flow_token_create_list_filter_detail(client: TestClient) -> None:
    login = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "admin123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
        "/veiculos",
        json={
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2022,
            "cor": "Prata",
            "placa": "ABC1D23",
            "preco_brl": "100000.00",
        },
        headers=headers,
    )
    created = create.json()

    listing = client.get("/veiculos?marca=Toyota&ano=2022&cor=Prata", headers=headers)
    detail = client.get(f"/veiculos/{created['id']}", headers=headers)

    assert login.status_code == 200
    assert create.status_code == 201
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert detail.status_code == 200
    assert detail.json()["placa"] == "ABC1D23"
