import pytest
from fastapi.testclient import TestClient

SYNDICAT_DATA = {
    "nom": "Résidence du Parc",
    "adresse": "500 Avenue du Parc",
    "ville": "Québec",
    "code_postal": "G1K 2S5",
    "nombre_unites": 12,
}

UNITE_DATA = {
    "numero": "101",
    "etage": 1,
    "superficie_m2": 75.5,
    "quote_part": 8.33,
    "description": "Condo 3½ avec balcon",
}


@pytest.fixture(name="syndicat_id")
def syndicat_id_fixture(client: TestClient, auth_headers: dict):
    """Crée un syndicat et retourne son ID"""
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    return resp.json()["id"]


def test_create_unite(client: TestClient, auth_headers: dict, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/unites",
        json=UNITE_DATA,
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["numero"] == "101"
    assert data["etage"] == 1
    assert data["superficie_m2"] == 75.5
    assert data["quote_part"] == 8.33
    assert data["syndicat_id"] == syndicat_id


def test_create_unite_unauthenticated(client: TestClient, syndicat_id: str):
    response = client.post(f"/syndicats/{syndicat_id}/unites", json=UNITE_DATA)
    assert response.status_code == 401


def test_list_unites(client: TestClient, auth_headers: dict, syndicat_id: str):
    client.post(
        f"/syndicats/{syndicat_id}/unites",
        json=UNITE_DATA,
        headers=auth_headers,
    )
    client.post(
        f"/syndicats/{syndicat_id}/unites",
        json={**UNITE_DATA, "numero": "102"},
        headers=auth_headers,
    )
    response = client.get(f"/syndicats/{syndicat_id}/unites", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_unite(client: TestClient, auth_headers: dict, syndicat_id: str):
    create_resp = client.post(
        f"/syndicats/{syndicat_id}/unites",
        json=UNITE_DATA,
        headers=auth_headers,
    )
    unite_id = create_resp.json()["id"]
    response = client.get(f"/unites/{unite_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["numero"] == "101"


def test_update_unite(client: TestClient, auth_headers: dict, syndicat_id: str):
    create_resp = client.post(
        f"/syndicats/{syndicat_id}/unites",
        json=UNITE_DATA,
        headers=auth_headers,
    )
    unite_id = create_resp.json()["id"]
    response = client.put(
        f"/unites/{unite_id}",
        json={"superficie_m2": 80.0, "description": "Rénové en 2026"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["superficie_m2"] == 80.0
    assert response.json()["description"] == "Rénové en 2026"


def test_duplicate_unite_numero(client: TestClient, auth_headers: dict, syndicat_id: str):
    client.post(
        f"/syndicats/{syndicat_id}/unites",
        json=UNITE_DATA,
        headers=auth_headers,
    )
    response = client.post(
        f"/syndicats/{syndicat_id}/unites",
        json=UNITE_DATA,
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "existe déjà" in response.json()["detail"]


def test_create_unite_invalid_syndicat(client: TestClient, auth_headers: dict):
    response = client.post(
        "/syndicats/00000000-0000-0000-0000-000000000000/unites",
        json=UNITE_DATA,
        headers=auth_headers,
    )
    assert response.status_code == 404
