"""
Tests bout en bout (E2E) complets pour SyndiPro.
Simule un parcours utilisateur complet : inscription → syndicat → unités →
finances → assemblée → vote → maintenance → documents → annonces → Loi 16.
"""

from fastapi.testclient import TestClient


def test_full_user_journey(client: TestClient):
    """Test bout en bout : parcours complet d'un administrateur de copropriété"""

    # ══ 1. INSCRIPTION ══
    reg = client.post(
        "/auth/register",
        json={
            "email": "e2e.admin@syndipro.qc",
            "nom": "Tremblay",
            "prenom": "Jean-Pierre",
            "password": "MonMotDePasse123!",
        },
    )
    assert reg.status_code == 200
    assert reg.json()["id"]
    assert reg.json()["prenom"] == "Jean-Pierre"

    # ══ 2. CONNEXION ══
    login = client.post(
        "/auth/login",
        data={"username": "e2e.admin@syndipro.qc", "password": "MonMotDePasse123!"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify /me
    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "e2e.admin@syndipro.qc"

    # ══ 3. CRÉER UN SYNDICAT ══
    syndicat = client.post(
        "/syndicats/",
        json={
            "nom": "Les Érables du Plateau",
            "adresse": "1234 Avenue du Mont-Royal Est",
            "ville": "Montréal",
            "code_postal": "H2J 1Y7",
            "nombre_unites": 12,
            "numero_syndicat": "SYN-E2E-001",
        },
        headers=headers,
    )
    assert syndicat.status_code == 201
    syndicat_id = syndicat.json()["id"]

    # Verify auto-membership as president
    mes_syndicats = client.get("/users/me/syndicats", headers=headers)
    assert mes_syndicats.status_code == 200
    assert len(mes_syndicats.json()) == 1
    assert mes_syndicats.json()[0]["role_syndicat"] == "president"

    # ══ 4. AJOUTER DES UNITÉS ══
    unites_ids = []
    for i in range(1, 7):
        unite = client.post(
            f"/syndicats/{syndicat_id}/unites",
            json={
                "numero": f"{i}01",
                "etage": i,
                "superficie_m2": 65.0 + i * 5,
                "quote_part": round(100 / 12, 2),
            },
            headers=headers,
        )
        assert unite.status_code == 201
        unites_ids.append(unite.json()["id"])

    # List unites
    unites_list = client.get(f"/syndicats/{syndicat_id}/unites", headers=headers)
    assert unites_list.status_code == 200
    assert len(unites_list.json()) == 6

    # ══ 5. AJOUTER UN SECOND MEMBRE ══
    reg2 = client.post(
        "/auth/register",
        json={
            "email": "e2e.copro@syndipro.qc",
            "nom": "Gagnon",
            "prenom": "Marie",
            "password": "Test123!",
        },
    )
    user2_id = reg2.json()["id"]

    add_membre = client.post(
        f"/syndicats/{syndicat_id}/membres",
        json={"user_id": user2_id, "role_syndicat": "tresorier"},
        headers=headers,
    )
    assert add_membre.status_code == 201

    membres = client.get(f"/syndicats/{syndicat_id}/membres", headers=headers)
    assert len(membres.json()) == 2

    # ══ 6. FINANCES - DÉPENSES ══
    dep1 = client.post(
        f"/syndicats/{syndicat_id}/depenses",
        json={
            "description": "Déneigement janvier 2026",
            "montant": 2500.00,
            "categorie": "entretien",
            "date_depense": "2026-01-15",
            "fournisseur": "Déneigement Québec Inc.",
        },
        headers=headers,
    )
    assert dep1.status_code == 201

    dep2 = client.post(
        f"/syndicats/{syndicat_id}/depenses",
        json={
            "description": "Assurance habitation collective",
            "montant": 12000.00,
            "categorie": "assurance",
            "date_depense": "2026-01-01",
            "fournisseur": "Desjardins Assurances",
        },
        headers=headers,
    )
    assert dep2.status_code == 201

    # ══ 7. FINANCES - COTISATIONS ══
    cot = client.post(
        f"/syndicats/{syndicat_id}/cotisations",
        json={
            "unite_id": unites_ids[0],
            "montant": 375.00,
            "mois": 1,
            "annee": 2026,
            "date_echeance": "2026-01-01",
        },
        headers=headers,
    )
    assert cot.status_code == 201
    cot_id = cot.json()["id"]

    # Mark as paid
    update_cot = client.put(
        f"/cotisations/{cot_id}",
        json={"statut": "payee", "date_paiement": "2026-01-05"},
        headers=headers,
    )
    assert update_cot.status_code == 200
    assert update_cot.json()["statut"] == "payee"

    # ══ 8. FINANCES - FONDS DE PRÉVOYANCE ══
    fonds = client.post(
        f"/syndicats/{syndicat_id}/fonds-prevoyance",
        json={
            "solde_actuel": 85000.00,
            "contribution_mensuelle": 2500.00,
            "objectif_25_ans": 750000.00,
            "derniere_etude": "2025-06-01",
            "prochaine_etude": "2030-06-01",
        },
        headers=headers,
    )
    assert fonds.status_code == 201

    # ══ 9. BILAN FINANCIER ══
    bilan = client.get(f"/syndicats/{syndicat_id}/bilan", headers=headers)
    assert bilan.status_code == 200
    bilan_data = bilan.json()
    assert bilan_data["total_depenses"] == 14500.00
    assert bilan_data["fonds_prevoyance_solde"] == 85000.00

    # ══ 10. ASSEMBLÉE GÉNÉRALE ══
    ag = client.post(
        f"/syndicats/{syndicat_id}/assemblees",
        json={
            "titre": "Assemblée générale annuelle 2026",
            "description": "Budget, travaux, élection du CA.",
            "type_assemblee": "annuelle",
            "date_assemblee": "2026-05-15T19:00:00Z",
            "lieu": "Salle communautaire",
            "quorum_requis": 50.0,
        },
        headers=headers,
    )
    assert ag.status_code == 201
    ag_id = ag.json()["id"]

    # Add resolutions
    res1 = client.post(
        f"/assemblees/{ag_id}/resolutions",
        json={
            "titre": "Adoption du budget 2026-2027",
            "description": "Budget annuel estimé à 85 000$.",
            "ordre": 1,
        },
        headers=headers,
    )
    assert res1.status_code == 201
    res1_id = res1.json()["id"]

    res2 = client.post(
        f"/assemblees/{ag_id}/resolutions",
        json={
            "titre": "Remplacement de la toiture",
            "description": "Travaux estimés à 120 000$, financement sur 3 ans.",
            "ordre": 2,
        },
        headers=headers,
    )
    assert res2.status_code == 201
    res2_id = res2.json()["id"]

    # ══ 11. VOTES ══
    vote1 = client.post(
        f"/resolutions/{res1_id}/votes",
        json={"type_vote": "pour"},
        headers=headers,
    )
    assert vote1.status_code == 201

    vote2 = client.post(
        f"/resolutions/{res2_id}/votes",
        json={"type_vote": "contre"},
        headers=headers,
    )
    assert vote2.status_code == 201

    # Check results
    resultat = client.get(f"/resolutions/{res1_id}/resultats", headers=headers)
    assert resultat.status_code == 200
    assert resultat.json()["pour"] == 1

    # Check full detail
    detail = client.get(f"/assemblees/{ag_id}/detail", headers=headers)
    assert detail.status_code == 200
    assert len(detail.json()["resolutions"]) == 2

    # ══ 12. MAINTENANCE ══
    demande = client.post(
        f"/syndicats/{syndicat_id}/maintenance",
        json={
            "titre": "Fuite d'eau au plafond unité 201",
            "description": "Infiltration d'eau visible au plafond de la cuisine.",
            "urgence": "haute",
        },
        headers=headers,
    )
    assert demande.status_code == 201
    demande_id = demande.json()["id"]
    assert demande.json()["statut"] == "soumise"

    # Progress workflow
    en_cours = client.put(
        f"/maintenance/{demande_id}",
        json={"statut": "en_cours"},
        headers=headers,
    )
    assert en_cours.json()["statut"] == "en_cours"

    complete = client.put(
        f"/maintenance/{demande_id}",
        json={"statut": "completee"},
        headers=headers,
    )
    assert complete.json()["statut"] == "completee"
    assert complete.json()["date_completion"] is not None

    # ══ 13. DOCUMENTS ══
    doc = client.post(
        f"/syndicats/{syndicat_id}/documents",
        json={
            "nom": "Procès-verbal AG 2025",
            "categorie": "proces-verbal",
            "description": "PV de l'assemblée générale annuelle 2025.",
        },
        headers=headers,
    )
    assert doc.status_code == 201

    docs_list = client.get(f"/syndicats/{syndicat_id}/documents", headers=headers)
    assert docs_list.status_code == 200
    assert len(docs_list.json()) >= 1

    # ══ 14. COMMUNICATIONS ══
    annonce = client.post(
        f"/syndicats/{syndicat_id}/annonces",
        json={
            "titre": "Bienvenue sur SyndiPro!",
            "contenu": "Notre syndicat utilise maintenant SyndiPro pour la gestion.",
            "est_epinglee": True,
        },
        headers=headers,
    )
    assert annonce.status_code == 201
    assert annonce.json()["est_epinglee"] is True

    annonces_list = client.get(f"/syndicats/{syndicat_id}/annonces", headers=headers)
    assert len(annonces_list.json()) >= 1

    # ══ 15. LOI 16 - COMPOSANTES ══
    comp1 = client.post(
        f"/syndicats/{syndicat_id}/composantes",
        json={
            "nom": "Toiture multicouche élastomère",
            "categorie": "toiture",
            "annee_installation": 2015,
            "duree_vie_estimee": 25,
            "etat": "acceptable",
            "cout_remplacement_estime": 120000.0,
            "derniere_inspection": "2025-09-15",
        },
        headers=headers,
    )
    assert comp1.status_code == 201
    comp1_id = comp1.json()["id"]

    comp2 = client.post(
        f"/syndicats/{syndicat_id}/composantes",
        json={
            "nom": "Système de chauffage central",
            "categorie": "mecanique",
            "annee_installation": 2010,
            "duree_vie_estimee": 20,
            "etat": "a_surveiller",
            "cout_remplacement_estime": 85000.0,
        },
        headers=headers,
    )
    assert comp2.status_code == 201

    # ══ 16. LOI 16 - CARNET D'ENTRETIEN ══
    entree = client.post(
        f"/syndicats/{syndicat_id}/carnet",
        json={
            "composante_id": comp1_id,
            "type_intervention": "inspection",
            "description": "Inspection annuelle de la toiture - état satisfaisant.",
            "date_intervention": "2026-03-15",
            "cout": 1500.00,
            "effectue_par": "Genispec Inc.",
        },
        headers=headers,
    )
    assert entree.status_code == 201

    # ══ 17. LOI 16 - SCORE DE CONFORMITÉ ══
    conformite = client.post(f"/syndicats/{syndicat_id}/conformite/evaluer", headers=headers)
    assert conformite.status_code == 200
    score_data = conformite.json()
    assert score_data["score"]["score_global"] > 0
    assert score_data["nombre_composantes"] == 2
    assert score_data["nombre_entrees_carnet"] == 1
    assert score_data["score"]["carnet_entretien_ok"] is True
    assert score_data["score"]["fonds_prevoyance_ok"] is True

    # Check critiques
    critiques = client.get(f"/syndicats/{syndicat_id}/composantes/critiques", headers=headers)
    assert critiques.status_code == 200
    assert len(critiques.json()) == 1  # chauffage a_surveiller
    assert critiques.json()[0]["nom"] == "Système de chauffage central"

    # ══ 18. VERIFICATION FINALE ══
    # Verify syndicat still accessible
    final_syndicat = client.get(f"/syndicats/{syndicat_id}", headers=headers)
    assert final_syndicat.status_code == 200
    assert final_syndicat.json()["nom"] == "Les Érables du Plateau"

    # Health check
    health = client.get("/")
    assert health.json()["status"] == "ok"


def test_multi_syndicat_user(client: TestClient):
    """Test qu'un utilisateur peut gérer plusieurs syndicats"""
    # Register
    client.post(
        "/auth/register",
        json={
            "email": "multi@syndipro.qc",
            "nom": "Roy",
            "prenom": "Luc",
            "password": "Test123!",
        },
    )
    login = client.post(
        "/auth/login",
        data={"username": "multi@syndipro.qc", "password": "Test123!"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # Create 3 syndicats
    ids = []
    for i, (nom, unites) in enumerate(
        [("Petit condo", 5), ("Moyen condo", 50), ("Grand condo", 100)]
    ):
        resp = client.post(
            "/syndicats/",
            json={
                "nom": nom,
                "adresse": f"{100 + i} Rue Test",
                "ville": "Montréal",
                "code_postal": "H2X 1Y1",
                "nombre_unites": unites,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        ids.append(resp.json()["id"])

    # Verify user is president of all 3
    mes = client.get("/users/me/syndicats", headers=headers)
    assert len(mes.json()) == 3
    for m in mes.json():
        assert m["role_syndicat"] == "president"

    # Each syndicat should be independent
    for sid in ids:
        syndicat = client.get(f"/syndicats/{sid}", headers=headers)
        assert syndicat.status_code == 200


def test_unauthorized_access_blocked(client: TestClient):
    """Test que toutes les routes protégées bloquent les accès non authentifiés"""
    protected_routes = [
        ("GET", "/syndicats/"),
        ("POST", "/syndicats/"),
        ("GET", "/users/me/syndicats"),
        ("GET", "/auth/me"),
    ]
    for method, route in protected_routes:
        if method == "GET":
            resp = client.get(route)
        else:
            resp = client.post(route, json={})
        assert resp.status_code == 401, f"{method} {route} should be 401"
