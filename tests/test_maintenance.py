import pytest
from fastapi.testclient import TestClient

SYNDICAT_DATA = {
    "nom": "Résidence du Parc Lafontaine",
    "adresse": "900 Rue Sherbrooke Est",
    "ville": "Montréal",
    "code_postal": "H2L 1L2",
    "nombre_unites": 48,
}


@pytest.fixture(name="syndicat_id")
def syndicat_id_fixture(client: TestClient, auth_headers: dict):
    """Crée un syndicat et retourne son ID"""
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    return resp.json()["id"]


# ── Tests Demandes de maintenance ──────────────────────────────────


def test_create_demande_maintenance(client: TestClient, auth_headers: dict, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/maintenance",
        json={
            "titre": "Fuite d'eau au sous-sol",
            "description": "Infiltration d'eau visible au plafond du stationnement P1.",
            "urgence": "haute",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["titre"] == "Fuite d'eau au sous-sol"
    assert data["urgence"] == "haute"
    assert data["statut"] == "soumise"
    assert data["syndicat_id"] == syndicat_id
    assert data["assignee_a"] is None
    assert data["date_completion"] is None


def test_create_demande_maintenance_unauthenticated(client: TestClient, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/maintenance",
        json={
            "titre": "Ampoule brûlée",
            "description": "Ampoule brûlée dans le corridor du 3e étage.",
        },
    )
    assert response.status_code == 401


def test_create_demande_default_urgence(client: TestClient, auth_headers: dict, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/maintenance",
        json={
            "titre": "Peinture écaillée",
            "description": "Peinture qui s'écaille dans le hall d'entrée principal.",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["urgence"] == "normale"


def test_list_demandes_maintenance(client: TestClient, auth_headers: dict, syndicat_id: str):
    demandes = [
        {
            "titre": "Porte de garage défectueuse",
            "description": "La porte du stationnement ne ferme plus correctement.",
            "urgence": "haute",
        },
        {
            "titre": "Éclairage extérieur",
            "description": "Deux lampadaires ne fonctionnent plus dans le jardin.",
            "urgence": "basse",
        },
        {
            "titre": "Ascenseur bruyant",
            "description": "L'ascenseur fait un bruit anormal lors de la montée.",
            "urgence": "normale",
        },
    ]
    for demande in demandes:
        client.post(
            f"/syndicats/{syndicat_id}/maintenance",
            json=demande,
            headers=auth_headers,
        )
    response = client.get(f"/syndicats/{syndicat_id}/maintenance", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_update_demande_statut(client: TestClient, auth_headers: dict, syndicat_id: str):
    create_resp = client.post(
        f"/syndicats/{syndicat_id}/maintenance",
        json={
            "titre": "Robinet qui coule",
            "description": "Robinet de la salle commune qui coule en permanence.",
        },
        headers=auth_headers,
    )
    demande_id = create_resp.json()["id"]

    response = client.put(
        f"/maintenance/{demande_id}",
        json={"statut": "assignee", "assignee_a": "Plomberie Montréal Inc."},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["statut"] == "assignee"
    assert data["assignee_a"] == "Plomberie Montréal Inc."


def test_complete_demande_sets_date(client: TestClient, auth_headers: dict, syndicat_id: str):
    create_resp = client.post(
        f"/syndicats/{syndicat_id}/maintenance",
        json={
            "titre": "Vitre fissurée",
            "description": "Vitre fissurée dans la porte d'entrée principale.",
            "urgence": "urgente",
        },
        headers=auth_headers,
    )
    demande_id = create_resp.json()["id"]

    response = client.put(
        f"/maintenance/{demande_id}",
        json={"statut": "completee"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["statut"] == "completee"
    assert data["date_completion"] is not None


# ── Tests Documents ────────────────────────────────────────────────


def test_create_document(client: TestClient, auth_headers: dict, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/documents",
        json={
            "nom": "Procès-verbal AG 2025",
            "categorie": "proces-verbal",
            "description": "PV de l'assemblée générale annuelle du 15 juin 2025",
            "taille_octets": 245000,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Procès-verbal AG 2025"
    assert data["categorie"] == "proces-verbal"
    assert data["taille_octets"] == 245000
    assert data["syndicat_id"] == syndicat_id


def test_list_documents(client: TestClient, auth_headers: dict, syndicat_id: str):
    documents = [
        {"nom": "Contrat de déneigement 2025-2026", "categorie": "contrat"},
        {"nom": "Police d'assurance 2026", "categorie": "assurance"},
        {"nom": "Règlement de copropriété", "categorie": "reglement"},
    ]
    for doc in documents:
        client.post(
            f"/syndicats/{syndicat_id}/documents",
            json=doc,
            headers=auth_headers,
        )
    response = client.get(f"/syndicats/{syndicat_id}/documents", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_document(client: TestClient, auth_headers: dict, syndicat_id: str):
    create_resp = client.post(
        f"/syndicats/{syndicat_id}/documents",
        json={
            "nom": "Budget prévisionnel 2026-2027",
            "categorie": "financier",
            "description": "Budget approuvé lors de l'AG du 15 juin 2025",
        },
        headers=auth_headers,
    )
    document_id = create_resp.json()["id"]

    response = client.get(f"/documents/{document_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == document_id
    assert data["nom"] == "Budget prévisionnel 2026-2027"
    assert data["categorie"] == "financier"
