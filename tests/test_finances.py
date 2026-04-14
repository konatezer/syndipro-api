import pytest
from fastapi.testclient import TestClient

SYNDICAT_DATA = {
    "nom": "Condos du Vieux-Montréal",
    "adresse": "350 Rue Saint-Paul Ouest",
    "ville": "Montréal",
    "code_postal": "H2Y 2A6",
    "nombre_unites": 24,
}

UNITE_DATA = {
    "numero": "301",
    "etage": 3,
    "superficie_m2": 82.0,
    "quote_part": 4.17,
    "description": "Condo 4½ avec vue sur le fleuve",
}


@pytest.fixture(name="syndicat_id")
def syndicat_id_fixture(client: TestClient, auth_headers: dict):
    """Crée un syndicat et retourne son ID"""
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    return resp.json()["id"]


@pytest.fixture(name="unite_id")
def unite_id_fixture(client: TestClient, auth_headers: dict, syndicat_id: str):
    """Crée une unité et retourne son ID"""
    resp = client.post(
        f"/syndicats/{syndicat_id}/unites",
        json=UNITE_DATA,
        headers=auth_headers,
    )
    return resp.json()["id"]


# ── Tests Cotisations ───────────────────────────────────────────────


def test_create_cotisation(client: TestClient, auth_headers: dict, syndicat_id: str, unite_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/cotisations",
        json={
            "unite_id": unite_id,
            "montant": 375.00,
            "mois": 3,
            "annee": 2026,
            "date_echeance": "2026-03-01",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["montant"] == 375.00
    assert data["mois"] == 3
    assert data["annee"] == 2026
    assert data["statut"] == "en_attente"
    assert data["syndicat_id"] == syndicat_id
    assert data["unite_id"] == unite_id


def test_create_cotisation_unauthenticated(client: TestClient, syndicat_id: str, unite_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/cotisations",
        json={
            "unite_id": unite_id,
            "montant": 375.00,
            "mois": 3,
            "annee": 2026,
            "date_echeance": "2026-03-01",
        },
    )
    assert response.status_code == 401


def test_list_cotisations(client: TestClient, auth_headers: dict, syndicat_id: str, unite_id: str):
    # Crée des cotisations pour janvier, février, mars
    for mois in [1, 2, 3]:
        client.post(
            f"/syndicats/{syndicat_id}/cotisations",
            json={
                "unite_id": unite_id,
                "montant": 375.00,
                "mois": mois,
                "annee": 2026,
                "date_echeance": f"2026-{mois:02d}-01",
            },
            headers=auth_headers,
        )
    response = client.get(f"/syndicats/{syndicat_id}/cotisations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_update_cotisation_statut_payee(
    client: TestClient, auth_headers: dict, syndicat_id: str, unite_id: str
):
    create_resp = client.post(
        f"/syndicats/{syndicat_id}/cotisations",
        json={
            "unite_id": unite_id,
            "montant": 425.50,
            "mois": 4,
            "annee": 2026,
            "date_echeance": "2026-04-01",
        },
        headers=auth_headers,
    )
    cotisation_id = create_resp.json()["id"]

    response = client.put(
        f"/cotisations/{cotisation_id}",
        json={"statut": "payee", "date_paiement": "2026-03-28"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["statut"] == "payee"
    assert data["date_paiement"] == "2026-03-28"


# ── Tests Dépenses ──────────────────────────────────────────────────


def test_create_depense(client: TestClient, auth_headers: dict, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/depenses",
        json={
            "description": "Déneigement stationnement et trottoirs - hiver 2026",
            "montant": 2850.00,
            "categorie": "entretien",
            "date_depense": "2026-02-15",
            "fournisseur": "Déneigement Laval Inc.",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Déneigement stationnement et trottoirs - hiver 2026"
    assert data["montant"] == 2850.00
    assert data["categorie"] == "entretien"
    assert data["fournisseur"] == "Déneigement Laval Inc."


def test_list_depenses(client: TestClient, auth_headers: dict, syndicat_id: str):
    depenses = [
        {
            "description": "Assurance habitation collective",
            "montant": 12500.00,
            "categorie": "assurance",
            "date_depense": "2026-01-01",
            "fournisseur": "Desjardins Assurances",
        },
        {
            "description": "Hydro-Québec — électricité parties communes",
            "montant": 1450.75,
            "categorie": "energie",
            "date_depense": "2026-02-01",
            "fournisseur": "Hydro-Québec",
        },
        {
            "description": "Honoraires comptable pour audit annuel",
            "montant": 3200.00,
            "categorie": "professionnel",
            "date_depense": "2026-03-15",
            "fournisseur": "Raymond Chabot Grant Thornton",
        },
    ]
    for depense in depenses:
        client.post(
            f"/syndicats/{syndicat_id}/depenses",
            json=depense,
            headers=auth_headers,
        )
    response = client.get(f"/syndicats/{syndicat_id}/depenses", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_update_depense(client: TestClient, auth_headers: dict, syndicat_id: str):
    create_resp = client.post(
        f"/syndicats/{syndicat_id}/depenses",
        json={
            "description": "Réparation ascenseur",
            "montant": 4500.00,
            "categorie": "entretien",
            "date_depense": "2026-03-10",
            "fournisseur": "Otis Canada",
        },
        headers=auth_headers,
    )
    depense_id = create_resp.json()["id"]

    response = client.put(
        f"/depenses/{depense_id}",
        json={"montant": 5200.00, "description": "Réparation ascenseur — pièces + main-d'œuvre"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["montant"] == 5200.00
    assert "pièces" in data["description"]


# ── Tests Fonds de prévoyance ───────────────────────────────────────


def test_create_fonds_prevoyance(client: TestClient, auth_headers: dict, syndicat_id: str):
    response = client.post(
        f"/syndicats/{syndicat_id}/fonds-prevoyance",
        json={
            "solde_actuel": 85000.00,
            "contribution_mensuelle": 2500.00,
            "objectif_25_ans": 750000.00,
            "derniere_etude": "2024-06-15",
            "prochaine_etude": "2029-06-15",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["solde_actuel"] == 85000.00
    assert data["contribution_mensuelle"] == 2500.00
    assert data["objectif_25_ans"] == 750000.00
    assert data["syndicat_id"] == syndicat_id


def test_get_fonds_prevoyance(client: TestClient, auth_headers: dict, syndicat_id: str):
    client.post(
        f"/syndicats/{syndicat_id}/fonds-prevoyance",
        json={
            "solde_actuel": 85000.00,
            "contribution_mensuelle": 2500.00,
        },
        headers=auth_headers,
    )
    response = client.get(f"/syndicats/{syndicat_id}/fonds-prevoyance", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["solde_actuel"] == 85000.00


def test_update_fonds_prevoyance(client: TestClient, auth_headers: dict, syndicat_id: str):
    client.post(
        f"/syndicats/{syndicat_id}/fonds-prevoyance",
        json={
            "solde_actuel": 85000.00,
            "contribution_mensuelle": 2500.00,
        },
        headers=auth_headers,
    )
    response = client.put(
        f"/syndicats/{syndicat_id}/fonds-prevoyance",
        json={"solde_actuel": 87500.00, "contribution_mensuelle": 3000.00},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["solde_actuel"] == 87500.00
    assert data["contribution_mensuelle"] == 3000.00


def test_duplicate_fonds_prevoyance(client: TestClient, auth_headers: dict, syndicat_id: str):
    client.post(
        f"/syndicats/{syndicat_id}/fonds-prevoyance",
        json={"solde_actuel": 85000.00, "contribution_mensuelle": 2500.00},
        headers=auth_headers,
    )
    response = client.post(
        f"/syndicats/{syndicat_id}/fonds-prevoyance",
        json={"solde_actuel": 50000.00, "contribution_mensuelle": 1000.00},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "déjà" in response.json()["detail"]


# ── Tests Bilan financier ───────────────────────────────────────────


def test_get_bilan_financier(
    client: TestClient, auth_headers: dict, syndicat_id: str, unite_id: str
):
    # Crée 3 cotisations (375$/mois) — 1 payée, 1 en retard, 1 en attente
    cotisation_ids = []
    for mois in [1, 2, 3]:
        resp = client.post(
            f"/syndicats/{syndicat_id}/cotisations",
            json={
                "unite_id": unite_id,
                "montant": 375.00,
                "mois": mois,
                "annee": 2026,
                "date_echeance": f"2026-{mois:02d}-01",
            },
            headers=auth_headers,
        )
        cotisation_ids.append(resp.json()["id"])

    # Marque janvier comme payée
    client.put(
        f"/cotisations/{cotisation_ids[0]}",
        json={"statut": "payee", "date_paiement": "2026-01-05"},
        headers=auth_headers,
    )
    # Marque février comme en retard
    client.put(
        f"/cotisations/{cotisation_ids[1]}",
        json={"statut": "en_retard"},
        headers=auth_headers,
    )

    # Crée des dépenses
    client.post(
        f"/syndicats/{syndicat_id}/depenses",
        json={
            "description": "Déneigement",
            "montant": 200.00,
            "categorie": "entretien",
            "date_depense": "2026-01-15",
        },
        headers=auth_headers,
    )

    # Crée le fonds de prévoyance
    client.post(
        f"/syndicats/{syndicat_id}/fonds-prevoyance",
        json={"solde_actuel": 50000.00, "contribution_mensuelle": 2000.00},
        headers=auth_headers,
    )

    # Récupère le bilan
    response = client.get(f"/syndicats/{syndicat_id}/bilan", headers=auth_headers)
    assert response.status_code == 200
    bilan = response.json()
    assert bilan["syndicat_id"] == syndicat_id
    assert bilan["total_cotisations_attendues"] == 1125.00  # 3 x 375
    assert bilan["total_cotisations_recues"] == 375.00  # 1 payée
    assert bilan["total_depenses"] == 200.00
    assert bilan["solde"] == 175.00  # 375 - 200
    assert bilan["cotisations_en_retard"] == 1
    assert bilan["cotisations_en_attente"] == 1
    assert bilan["fonds_prevoyance_solde"] == 50000.00
