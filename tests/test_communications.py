import pytest
from fastapi.testclient import TestClient

SYNDICAT_DATA = {
    "nom": "Les Jardins de la Rivière",
    "adresse": "500 Boulevard Gouin Ouest",
    "ville": "Montréal",
    "code_postal": "H3L 1K3",
    "nombre_unites": 30,
}


@pytest.fixture(name="syndicat_id")
def syndicat_id_fixture(client: TestClient, auth_headers: dict):
    """Crée un syndicat et retourne son ID"""
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    return resp.json()["id"]


# ── Tests Annonces ─────────────────────────────────────────────────


def test_create_annonce(client: TestClient, auth_headers: dict, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/annonces",
        json={
            "titre": "Travaux de toiture — semaine du 14 avril",
            "contenu": "Chers copropriétaires, veuillez noter que des travaux de réfection "
            "de la toiture débuteront le lundi 14 avril 2026. Durée estimée : 5 jours.",
            "est_epinglee": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["titre"] == "Travaux de toiture — semaine du 14 avril"
    assert data["est_epinglee"] is True
    assert data["syndicat_id"] == syndicat_id


def test_create_annonce_unauthenticated(client: TestClient, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/annonces",
        json={
            "titre": "Test",
            "contenu": "Contenu de test",
        },
    )
    assert response.status_code == 401


def test_list_annonces(client: TestClient, auth_headers: dict, syndicat_id: str):
    annonces = [
        {
            "titre": "Fermeture piscine — entretien annuel",
            "contenu": "La piscine sera fermée du 1er au 15 mai pour l'entretien annuel.",
        },
        {
            "titre": "Rappel — assemblée générale annuelle",
            "contenu": "L'assemblée générale annuelle aura lieu le 15 juin 2026 à 19h.",
            "est_epinglee": True,
        },
    ]
    for annonce in annonces:
        client.post(
            f"/syndicats/{syndicat_id}/annonces",
            json=annonce,
            headers=auth_headers,
        )
    response = client.get(f"/syndicats/{syndicat_id}/annonces", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_update_annonce(client: TestClient, auth_headers: dict, syndicat_id: str):
    create_resp = client.post(
        f"/syndicats/{syndicat_id}/annonces",
        json={
            "titre": "Avis de coupure d'eau",
            "contenu": "Coupure d'eau prévue le 20 avril de 9h à 12h.",
        },
        headers=auth_headers,
    )
    annonce_id = create_resp.json()["id"]

    response = client.put(
        f"/annonces/{annonce_id}",
        json={
            "contenu": "Coupure d'eau reportée au 22 avril de 9h à 14h.",
            "est_epinglee": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "22 avril" in data["contenu"]
    assert data["est_epinglee"] is True


def test_delete_annonce(client: TestClient, auth_headers: dict, syndicat_id: str):
    create_resp = client.post(
        f"/syndicats/{syndicat_id}/annonces",
        json={
            "titre": "Annonce temporaire",
            "contenu": "Cette annonce sera supprimée.",
        },
        headers=auth_headers,
    )
    annonce_id = create_resp.json()["id"]

    response = client.delete(f"/annonces/{annonce_id}", headers=auth_headers)
    assert response.status_code == 204

    # Vérifie que l'annonce n'est plus dans la liste
    list_resp = client.get(f"/syndicats/{syndicat_id}/annonces", headers=auth_headers)
    assert len(list_resp.json()) == 0


def test_default_not_pinned(client: TestClient, auth_headers: dict, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/annonces",
        json={
            "titre": "Information générale",
            "contenu": "Annonce non épinglée par défaut.",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["est_epinglee"] is False
