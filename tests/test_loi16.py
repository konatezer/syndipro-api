import pytest
from fastapi.testclient import TestClient

SYNDICAT_DATA = {
    "nom": "Copropriété Place Ville-Marie",
    "adresse": "1 Place Ville-Marie",
    "ville": "Montréal",
    "code_postal": "H3B 2B6",
    "nombre_unites": 120,
}


@pytest.fixture(name="syndicat_id")
def syndicat_id_fixture(client: TestClient, auth_headers: dict):
    """Crée un syndicat et retourne son ID"""
    resp = client.post("/syndicats/", json=SYNDICAT_DATA, headers=auth_headers)
    return resp.json()["id"]


@pytest.fixture(name="composante_toiture_id")
def composante_toiture_fixture(client: TestClient, auth_headers: dict, syndicat_id: str):
    """Crée une composante toiture et retourne son ID"""
    resp = client.post(
        f"/syndicats/{syndicat_id}/composantes",
        json={
            "nom": "Toiture multicouche",
            "categorie": "toiture",
            "description": "Toiture multicouche élastomère, 450 m²",
            "annee_installation": 2015,
            "duree_vie_estimee": 25,
            "etat": "acceptable",
            "cout_remplacement_estime": 85000.0,
            "derniere_inspection": "2025-09-15",
            "prochaine_inspection": "2026-09-15",
        },
        headers=auth_headers,
    )
    return resp.json()["id"]


# ── Tests Composantes d'immeuble ─────────────────────────────────


def test_create_composante_toiture(client: TestClient, auth_headers: dict, syndicat_id: str):
    """Test création d'une composante toiture typique au Québec"""
    response = client.post(
        f"/syndicats/{syndicat_id}/composantes",
        json={
            "nom": "Membrane de toiture",
            "categorie": "toiture",
            "description": "Membrane élastomère 2 plis sur isolant rigide",
            "annee_installation": 2018,
            "duree_vie_estimee": 25,
            "etat": "bon",
            "cout_remplacement_estime": 120000.0,
            "derniere_inspection": "2025-06-01",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Membrane de toiture"
    assert data["categorie"] == "toiture"
    assert data["etat"] == "bon"
    assert data["cout_remplacement_estime"] == 120000.0
    assert data["syndicat_id"] == syndicat_id


def test_create_composante_ascenseur(client: TestClient, auth_headers: dict, syndicat_id: str):
    """Test création d'une composante ascenseur"""
    response = client.post(
        f"/syndicats/{syndicat_id}/composantes",
        json={
            "nom": "Ascenseur principal",
            "categorie": "ascenseur",
            "description": "Ascenseur hydraulique Otis, capacité 2000 lb, 8 étages",
            "annee_installation": 2005,
            "duree_vie_estimee": 30,
            "etat": "a_surveiller",
            "cout_remplacement_estime": 250000.0,
            "derniere_inspection": "2025-03-20",
            "prochaine_inspection": "2025-09-20",
            "notes": (
                "Bruit anormal signalé par les résidents, "
                "à vérifier lors de la prochaine inspection."
            ),
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["categorie"] == "ascenseur"
    assert data["etat"] == "a_surveiller"
    assert data["annee_installation"] == 2005


def test_create_composante_unauthenticated(client: TestClient, syndicat_id: str):
    """Test que la création de composante requiert l'authentification"""
    response = client.post(
        f"/syndicats/{syndicat_id}/composantes",
        json={
            "nom": "Système de chauffage",
            "categorie": "mecanique",
        },
    )
    assert response.status_code == 401


def test_list_composantes(client: TestClient, auth_headers: dict, syndicat_id: str):
    """Test listing de composantes multiples d'un immeuble québécois"""
    composantes = [
        {
            "nom": "Système de chauffage central",
            "categorie": "mecanique",
            "annee_installation": 2010,
            "etat": "acceptable",
            "cout_remplacement_estime": 75000.0,
        },
        {
            "nom": "Panneau électrique principal",
            "categorie": "electrique",
            "annee_installation": 2008,
            "etat": "bon",
        },
        {
            "nom": "Colonne de plomberie nord",
            "categorie": "plomberie",
            "annee_installation": 1995,
            "etat": "a_remplacer",
            "cout_remplacement_estime": 45000.0,
        },
        {
            "nom": "Stationnement souterrain P1",
            "categorie": "stationnement",
            "annee_installation": 1990,
            "etat": "critique",
            "cout_remplacement_estime": 350000.0,
        },
    ]
    for comp in composantes:
        client.post(
            f"/syndicats/{syndicat_id}/composantes",
            json=comp,
            headers=auth_headers,
        )

    response = client.get(f"/syndicats/{syndicat_id}/composantes", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4


def test_update_composante_etat(client: TestClient, auth_headers: dict, composante_toiture_id: str):
    """Test mise à jour de l'état d'une composante après inspection"""
    response = client.put(
        f"/composantes/{composante_toiture_id}",
        json={
            "etat": "a_surveiller",
            "notes": (
                "Fissures mineures détectées lors de "
                "l'inspection du 15 septembre. Suivi requis au printemps."
            ),
            "prochaine_inspection": "2026-04-01",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["etat"] == "a_surveiller"
    assert "Fissures mineures" in data["notes"]


def test_composantes_critiques(client: TestClient, auth_headers: dict, syndicat_id: str):
    """Test filtrage des composantes en état critique"""
    composantes = [
        {"nom": "Fondations", "categorie": "structure", "etat": "bon"},
        {"nom": "Fenêtres façade nord", "categorie": "enveloppe", "etat": "a_remplacer"},
        {"nom": "Système de ventilation", "categorie": "mecanique", "etat": "critique"},
        {"nom": "Aménagement paysager", "categorie": "amenagement", "etat": "acceptable"},
        {"nom": "Balcons 3e étage", "categorie": "structure", "etat": "a_surveiller"},
    ]
    for comp in composantes:
        client.post(
            f"/syndicats/{syndicat_id}/composantes",
            json=comp,
            headers=auth_headers,
        )

    response = client.get(f"/syndicats/{syndicat_id}/composantes/critiques", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # a_surveiller, a_remplacer, critique = 3 composantes
    assert len(data) == 3
    etats = {c["etat"] for c in data}
    assert etats == {"a_surveiller", "a_remplacer", "critique"}


# ── Tests Carnet d'entretien ──────────────────────────────────────


def test_create_entree_carnet(
    client: TestClient, auth_headers: dict, syndicat_id: str, composante_toiture_id: str
):
    """Test création d'une entrée de carnet d'entretien"""
    response = client.post(
        f"/syndicats/{syndicat_id}/carnet",
        json={
            "composante_id": composante_toiture_id,
            "type_intervention": "inspection",
            "description": (
                "Inspection annuelle de la toiture. Membrane en bon état, drain vérifié."
            ),
            "date_intervention": "2025-09-15",
            "cout": 450.0,
            "effectue_par": "Toitures Québec Inc.",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type_intervention"] == "inspection"
    assert data["cout"] == 450.0
    assert data["effectue_par"] == "Toitures Québec Inc."
    assert data["syndicat_id"] == syndicat_id
    assert data["composante_id"] == composante_toiture_id


def test_list_entrees_carnet(
    client: TestClient, auth_headers: dict, syndicat_id: str, composante_toiture_id: str
):
    """Test listing des entrées du carnet"""
    entrees = [
        {
            "composante_id": composante_toiture_id,
            "type_intervention": "inspection",
            "description": "Inspection printanière de la toiture",
            "date_intervention": "2025-04-10",
            "cout": 350.0,
            "effectue_par": "Toitures Québec Inc.",
        },
        {
            "composante_id": composante_toiture_id,
            "type_intervention": "reparation",
            "description": "Réparation de fissures mineures sur la membrane",
            "date_intervention": "2025-05-20",
            "cout": 1200.0,
            "effectue_par": "Toitures Québec Inc.",
        },
        {
            "composante_id": composante_toiture_id,
            "type_intervention": "entretien",
            "description": "Nettoyage des drains et gouttières avant l'hiver",
            "date_intervention": "2025-10-15",
            "cout": 275.0,
            "effectue_par": "Entretien Montréal",
        },
    ]
    for entree in entrees:
        client.post(
            f"/syndicats/{syndicat_id}/carnet",
            json=entree,
            headers=auth_headers,
        )

    response = client.get(f"/syndicats/{syndicat_id}/carnet", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


# ── Tests Score de conformité ─────────────────────────────────────


def test_get_conformite_empty(client: TestClient, auth_headers: dict, syndicat_id: str):
    """Test score de conformité pour un syndicat sans données"""
    response = client.get(f"/syndicats/{syndicat_id}/conformite", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["score"]["score_global"] == 0
    assert data["nombre_composantes"] == 0
    assert data["nombre_entrees_carnet"] == 0
    assert data["composantes_critiques"] == 0


def test_evaluer_conformite_score_partiel(
    client: TestClient, auth_headers: dict, syndicat_id: str, composante_toiture_id: str
):
    """Test calcul du score avec des données partielles (composantes + entrées récentes)"""
    # Ajouter une entrée de carnet récente
    client.post(
        f"/syndicats/{syndicat_id}/carnet",
        json={
            "composante_id": composante_toiture_id,
            "type_intervention": "inspection",
            "description": "Inspection de la toiture après les pluies de printemps",
            "date_intervention": "2026-03-15",
            "effectue_par": "Inspections Bâtiment QC",
        },
        headers=auth_headers,
    )

    # Évaluer la conformité
    response = client.post(f"/syndicats/{syndicat_id}/conformite/evaluer", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    score = data["score"]
    # Composantes: 20pts + Entrées récentes: 20pts + Couverture > 80%: 20pts = 60
    # Pas de fonds de prévoyance, pas d'étude
    assert score["score_global"] == 60
    assert score["carnet_entretien_ok"] is True
    assert score["fonds_prevoyance_ok"] is False
    assert score["etude_fonds_a_jour"] is False
    assert score["recommandations"] is not None
    assert data["nombre_composantes"] == 1
    assert data["nombre_entrees_carnet"] == 1


def test_evaluer_conformite_score_complet(client: TestClient, auth_headers: dict, syndicat_id: str):
    """Test calcul du score complet (100%) avec toutes les conditions remplies"""
    # Créer une composante avec inspection récente
    resp = client.post(
        f"/syndicats/{syndicat_id}/composantes",
        json={
            "nom": "Système de chauffage au gaz",
            "categorie": "mecanique",
            "annee_installation": 2020,
            "duree_vie_estimee": 20,
            "etat": "bon",
            "derniere_inspection": "2026-01-15",
        },
        headers=auth_headers,
    )
    comp_id = resp.json()["id"]

    # Ajouter une entrée récente au carnet
    client.post(
        f"/syndicats/{syndicat_id}/carnet",
        json={
            "composante_id": comp_id,
            "type_intervention": "entretien",
            "description": "Entretien annuel du système de chauffage",
            "date_intervention": "2026-01-15",
            "cout": 600.0,
            "effectue_par": "Chauffage Montréal",
        },
        headers=auth_headers,
    )

    # Créer un fonds de prévoyance avec étude récente
    client.post(
        f"/syndicats/{syndicat_id}/fonds-prevoyance",
        json={
            "solde_actuel": 250000.0,
            "contribution_mensuelle": 5000.0,
            "objectif_25_ans": 1500000.0,
            "derniere_etude": "2024-06-15",
            "prochaine_etude": "2029-06-15",
        },
        headers=auth_headers,
    )

    # Évaluer la conformité
    response = client.post(f"/syndicats/{syndicat_id}/conformite/evaluer", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    score = data["score"]
    # Composantes: 20 + Entrées: 20 + Fonds: 20 + Étude: 20 + Couverture 100%: 20 = 100
    assert score["score_global"] == 100
    assert score["carnet_entretien_ok"] is True
    assert score["fonds_prevoyance_ok"] is True
    assert score["etude_fonds_a_jour"] is True
    assert score["attestation_disponible"] is True
    assert score["recommandations"] is None
