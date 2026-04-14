from fastapi.testclient import TestClient

SYNDICAT_DATA = {
    "nom": "Le Domaine Royal",
    "adresse": "789 Boulevard René-Lévesque",
    "ville": "Québec",
    "code_postal": "G1R 2B5",
    "nombre_unites": 30,
}


def _create_second_user(client: TestClient):
    """Crée un second utilisateur et retourne son ID"""
    resp = client.post(
        "/auth/register",
        json={
            "email": "second@syndipro.qc",
            "nom": "Gagnon",
            "prenom": "Marie",
            "password": "MotDePasse123!",
        },
    )
    return resp.json()["id"]


def test_creator_becomes_president(client: TestClient, auth_headers: dict):
    """Quand on crée un syndicat, le créateur doit être ajouté comme président"""
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    syndicat_id = resp.json()["id"]

    membres = client.get(f"/syndicats/{syndicat_id}/membres", headers=auth_headers)
    assert membres.status_code == 200
    data = membres.json()
    assert len(data) == 1
    assert data[0]["role_syndicat"] == "president"
    assert data[0]["user_email"] == "test@syndipro.qc"


def test_add_membre(client: TestClient, auth_headers: dict):
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    syndicat_id = resp.json()["id"]
    second_user_id = _create_second_user(client)

    add_resp = client.post(
        f"/syndicats/{syndicat_id}/membres",
        json={"user_id": second_user_id, "role_syndicat": "coproprietaire"},
        headers=auth_headers,
    )
    assert add_resp.status_code == 201
    assert add_resp.json()["role_syndicat"] == "coproprietaire"


def test_add_duplicate_membre(client: TestClient, auth_headers: dict):
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    syndicat_id = resp.json()["id"]
    second_user_id = _create_second_user(client)

    client.post(
        f"/syndicats/{syndicat_id}/membres",
        json={"user_id": second_user_id},
        headers=auth_headers,
    )
    dup_resp = client.post(
        f"/syndicats/{syndicat_id}/membres",
        json={"user_id": second_user_id},
        headers=auth_headers,
    )
    assert dup_resp.status_code == 400
    assert "déjà membre" in dup_resp.json()["detail"]


def test_my_syndicats(client: TestClient, auth_headers: dict):
    client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    resp = client.get("/users/me/syndicats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["syndicat_nom"] == SYNDICAT_DATA["nom"]
    assert data[0]["role_syndicat"] == "president"


def test_update_membre_role(client: TestClient, auth_headers: dict):
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    syndicat_id = resp.json()["id"]
    second_user_id = _create_second_user(client)

    add_resp = client.post(
        f"/syndicats/{syndicat_id}/membres",
        json={"user_id": second_user_id},
        headers=auth_headers,
    )
    membre_id = add_resp.json()["id"]

    update_resp = client.put(
        f"/membres/{membre_id}",
        json={"role_syndicat": "tresorier"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["role_syndicat"] == "tresorier"


def test_remove_membre(client: TestClient, auth_headers: dict):
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    syndicat_id = resp.json()["id"]
    second_user_id = _create_second_user(client)

    add_resp = client.post(
        f"/syndicats/{syndicat_id}/membres",
        json={"user_id": second_user_id},
        headers=auth_headers,
    )
    membre_id = add_resp.json()["id"]

    del_resp = client.delete(f"/membres/{membre_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    membres = client.get(f"/syndicats/{syndicat_id}/membres", headers=auth_headers)
    emails = [m["user_email"] for m in membres.json()]
    assert "second@syndipro.qc" not in emails
