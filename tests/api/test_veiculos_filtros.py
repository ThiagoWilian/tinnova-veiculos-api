from fastapi.testclient import TestClient


def test_list_combined_filters_and_sort(
    client: TestClient,
    admin_headers: dict[str, str],
    ) -> None:
    payloads = [
        {
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2022,
            "cor": "Prata",
            "placa": "ABC1D23",
            "preco_brl": "100000.00",
        },
        {
            "marca": "Toyota",
            "modelo": "Hilux",
            "ano": 2022,
            "cor": "Preto",
            "placa": "DEF4G56",
            "preco_brl": "250000.00",
        },
        {
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2020,
            "cor": "Prata",
            "placa": "HIJ7K89",
            "preco_brl": "120000.00",
        },
    ]
    for payload in payloads:
        client.post("/veiculos", json=payload, headers=admin_headers)

    response = client.get(
        "/veiculos?marca=Toyota&ano=2022&cor=Prata&minPreco=10000&maxPreco=30000&sort_by=preco_usd&sort_dir=asc",
        headers=admin_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["modelo"] == "Corolla"


def test_report_by_marca(
    client: TestClient,
    admin_headers: dict[str, str],
    ) -> None:
    client.post(
        "/veiculos",
        json={
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2022,
            "cor": "Prata",
            "placa": "ABC1D23",
            "preco_brl": "100000.00",
        },
        headers=admin_headers,
    )
    client.post(
        "/veiculos",
        json={
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2020,
            "cor": "Prata",
            "placa": "HIJ7K89",
            "preco_brl": "120000.00",
        },
        headers=admin_headers,
    )

    response = client.get("/veiculos/relatorios/por-marca", headers=admin_headers)

    assert response.status_code == 200
    assert response.json() == [
        {"marca": "Honda", "quantidade": 1},
        {"marca": "Toyota", "quantidade": 1},
    ]