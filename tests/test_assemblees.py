import pytest
from fastapi.testclient import TestClient

SYNDICAT_DATA = {
    "nom": "Le Plateau des Érables",
    "adresse": "1200 Avenue du Mont-Royal Est",
    "ville": "Montréal",
    "code_postal": "H2J 1Y8",
    "nombre_unites": 36,
}


@pytest.fixture(name="syndicat_id")
def syndicat_id_fixture(client: TestClient, auth_headers: dict):
    """Crée un syndicat et retourne son ID"""
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    return resp.json()["id"]


@pytest.fixture(name="assemblee_id")
def assemblee_id_fixture(client: TestClient, auth_headers: dict, syndicat_id: str):
    """Crée une assemblée et retourne son ID"""
    resp = client.post(
        f"/syndicats/{syndicat_id}/assemblees",
        json={
            "titre": "Assemblée générale annuelle 2026",
            "description": "AG annuelle du syndicat Le Plateau des Érables",
            "type_assemblee": "annuelle",
            "date_assemblee": "2026-06-15T19:00:00",
            "lieu": "Salle communautaire, 1200 Av. du Mont-Royal Est",
            "quorum_requis": 50.0,
        },
        headers=auth_headers,
    )
    return resp.json()["id"]


@pytest.fixture(name="resolution_id")
def resolution_id_fixture(client: TestClient, auth_headers: dict, assemblee_id: str):
    """Crée une résolution et retourne son ID"""
    resp = client.post(
        f"/assemblees/{assemblee_id}/resolutions",
        json={
            "titre": "Adoption du budget 2026-2027",
            "description": "Approbation du budget prévisionnel pour l'exercice 2026-2027",
            "ordre": 1,
        },
        headers=auth_headers,
    )
    return resp.json()["id"]


# ── Tests Assemblées ───────────────────────────────────────────────


def test_create_assemblee(client: TestClient, auth_headers: dict, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/assemblees",
        json={
            "titre": "Assemblée générale annuelle 2026",
            "description": "AG annuelle du syndicat Le Plateau des Érables",
            "type_assemblee": "annuelle",
            "date_assemblee": "2026-06-15T19:00:00",
            "lieu": "Salle communautaire, 1200 Av. du Mont-Royal Est",
            "quorum_requis": 50.0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["titre"] == "Assemblée générale annuelle 2026"
    assert data["type_assemblee"] == "annuelle"
    assert data["statut"] == "planifiee"
    assert data["quorum_requis"] == 50.0
    assert data["syndicat_id"] == syndicat_id


def test_create_assemblee_unauthenticated(client: TestClient, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/assemblees",
        json={
            "titre": "AG 2026",
            "type_assemblee": "annuelle",
            "date_assemblee": "2026-06-15T19:00:00",
        },
    )
    assert response.status_code == 401


def test_list_assemblees(client: TestClient, auth_headers: dict, syndicat_id: str):
    assemblees = [
        {
            "titre": "Assemblée générale annuelle 2026",
            "type_assemblee": "annuelle",
            "date_assemblee": "2026-06-15T19:00:00",
        },
        {
            "titre": "Assemblée spéciale — travaux urgents toiture",
            "type_assemblee": "speciale",
            "date_assemblee": "2026-09-20T18:30:00",
        },
    ]
    for ag in assemblees:
        client.post(
            f"/syndicats/{syndicat_id}/assemblees",
            json=ag,
            headers=auth_headers,
        )

    response = client.get(f"/syndicats/{syndicat_id}/assemblees", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_assemblee(client: TestClient, auth_headers: dict, assemblee_id: str):
    response = client.get(f"/assemblees/{assemblee_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == assemblee_id
    assert data["titre"] == "Assemblée générale annuelle 2026"


def test_update_assemblee_statut(client: TestClient, auth_headers: dict, assemblee_id: str):
    response = client.put(
        f"/assemblees/{assemblee_id}",
        json={"statut": "en_cours"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["statut"] == "en_cours"


# ── Tests Résolutions ──────────────────────────────────────────────


def test_add_resolution(client: TestClient, auth_headers: dict, assemblee_id: str):
    response = client.post(
        f"/assemblees/{assemblee_id}/resolutions",
        json={
            "titre": "Remplacement de la toiture",
            "description": "Approbation des travaux de remplacement de la toiture",
            "ordre": 1,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["titre"] == "Remplacement de la toiture"
    assert data["ordre"] == 1
    assert data["est_adoptee"] is None
    assert data["assemblee_id"] == assemblee_id


def test_add_multiple_resolutions(client: TestClient, auth_headers: dict, assemblee_id: str):
    resolutions = [
        {
            "titre": "Adoption du budget 2026-2027",
            "description": "Budget prévisionnel de 245 000 $",
            "ordre": 1,
        },
        {
            "titre": "Remplacement de la toiture",
            "description": "Travaux estimés à 185 000 $",
            "ordre": 2,
        },
        {
            "titre": "Élection des administrateurs",
            "description": "Renouvellement de deux postes au conseil d'administration",
            "ordre": 3,
        },
    ]
    for res in resolutions:
        resp = client.post(
            f"/assemblees/{assemblee_id}/resolutions",
            json=res,
            headers=auth_headers,
        )
        assert resp.status_code == 201


# ── Tests Votes ────────────────────────────────────────────────────


def test_submit_vote(client: TestClient, auth_headers: dict, resolution_id: str):
    response = client.post(
        f"/resolutions/{resolution_id}/votes",
        json={"type_vote": "pour"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type_vote"] == "pour"
    assert data["resolution_id"] == resolution_id


def test_prevent_duplicate_vote(client: TestClient, auth_headers: dict, resolution_id: str):
    # Premier vote
    client.post(
        f"/resolutions/{resolution_id}/votes",
        json={"type_vote": "pour"},
        headers=auth_headers,
    )

    # Deuxième vote — doit être refusé
    response = client.post(
        f"/resolutions/{resolution_id}/votes",
        json={"type_vote": "contre"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "déjà voté" in response.json()["detail"]


def test_get_resultat_vote(client: TestClient, auth_headers: dict, resolution_id: str):
    # Soumet un vote
    client.post(
        f"/resolutions/{resolution_id}/votes",
        json={"type_vote": "pour"},
        headers=auth_headers,
    )

    response = client.get(f"/resolutions/{resolution_id}/resultats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["pour"] == 1
    assert data["contre"] == 0
    assert data["abstention"] == 0
    assert data["est_adoptee"] is True
    assert data["resolution_id"] == resolution_id


# ── Tests Détail assemblée ────────────────────────────────────────


def test_get_assemblee_detail(client: TestClient, auth_headers: dict, assemblee_id: str):
    # Ajoute deux résolutions
    res1 = client.post(
        f"/assemblees/{assemblee_id}/resolutions",
        json={
            "titre": "Adoption du budget 2026-2027",
            "description": "Budget prévisionnel annuel",
            "ordre": 1,
        },
        headers=auth_headers,
    ).json()

    client.post(
        f"/assemblees/{assemblee_id}/resolutions",
        json={
            "titre": "Remplacement de la toiture",
            "description": "Approbation des travaux majeurs",
            "ordre": 2,
        },
        headers=auth_headers,
    )

    # Vote sur la première résolution
    client.post(
        f"/resolutions/{res1['id']}/votes",
        json={"type_vote": "pour"},
        headers=auth_headers,
    )

    # Récupère le détail complet
    response = client.get(f"/assemblees/{assemblee_id}/detail", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == assemblee_id
    assert data["titre"] == "Assemblée générale annuelle 2026"
    assert len(data["resolutions"]) == 2

    # Première résolution a un résultat de vote
    res_budget = data["resolutions"][0]
    assert res_budget["titre"] == "Adoption du budget 2026-2027"
    assert res_budget["resultat"] is not None
    assert res_budget["resultat"]["pour"] == 1

    # Deuxième résolution n'a pas encore de vote
    res_toiture = data["resolutions"][1]
    assert res_toiture["titre"] == "Remplacement de la toiture"
    assert res_toiture["resultat"] is None


def test_get_assemblee_detail_no_resolutions(
    client: TestClient, auth_headers: dict, assemblee_id: str
):
    response = client.get(f"/assemblees/{assemblee_id}/detail", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["resolutions"] == []
