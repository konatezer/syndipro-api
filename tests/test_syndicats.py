from fastapi.testclient import TestClient

SYNDICAT_DATA = {
    "nom": "Les Jardins du Plateau",
    "adresse": "1234 Rue Saint-Denis",
    "ville": "Montréal",
    "code_postal": "H2X 3K8",
    "nombre_unites": 24,
    "numero_syndicat": "SYN-001",
}


def test_create_syndicat(client: TestClient, auth_headers: dict):
    response = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == SYNDICAT_DATA["nom"]
    assert data["adresse"] == SYNDICAT_DATA["adresse"]
    assert data["ville"] == "Montréal"
    assert data["nombre_unites"] == 24
    assert data["is_active"] is True


def test_create_syndicat_unauthenticated(client: TestClient):
    response = client.post("/syndicats/", json=SYNDICAT_DATA)
    assert response.status_code == 401


def test_list_syndicats(client: TestClient, auth_headers: dict):
    client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    response = client.get("/syndicats/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["nom"] == SYNDICAT_DATA["nom"]


def test_get_syndicat(client: TestClient, auth_headers: dict):
    create_resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    syndicat_id = create_resp.json()["id"]
    response = client.get(f"/syndicats/{syndicat_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == syndicat_id


def test_update_syndicat(client: TestClient, auth_headers: dict):
    create_resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    syndicat_id = create_resp.json()["id"]
    response = client.put(
        f"/syndicats/{syndicat_id}",
        json={"nom": "Les Jardins Rénovés"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["nom"] == "Les Jardins Rénovés"


def test_delete_syndicat(client: TestClient, auth_headers: dict):
    create_resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    syndicat_id = create_resp.json()["id"]
    delete_resp = client.delete(f"/syndicats/{syndicat_id}", headers=auth_headers)
    assert delete_resp.status_code == 204
    get_resp = client.get(f"/syndicats/{syndicat_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_get_nonexistent_syndicat(client: TestClient, auth_headers: dict):
    response = client.get(
        "/syndicats/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_duplicate_numero_syndicat(client: TestClient, auth_headers: dict):
    client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    response = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    assert response.status_code == 400
    assert "existe déjà" in response.json()["detail"]
