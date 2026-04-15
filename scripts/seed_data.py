"""
Script de seed data pour SyndiPro.
Crée un portefeuille réaliste de copropriétés québécoises avec membres,
unités, finances, assemblées, maintenance, documents, annonces et composantes Loi 16.

Usage:
    cd syndipro-api
    uv run python scripts/seed_data.py
"""

import random
from datetime import date, datetime, timedelta, timezone

from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import DATABASE_URL
from app.core.security import hash_password
from app.models.assemblee import Assemblee, Resolution
from app.models.communication import Annonce
from app.models.finance import Cotisation, Depense, FondsPrevoyance
from app.models.loi16 import ComposanteImmeuble, EntreeCarnet
from app.models.maintenance import DemandeMaintenance, Document
from app.models.membre import MembreSyndicat, RoleSyndicat
from app.models.syndicat import Syndicat
from app.models.unite import Unite
from app.models.user import RoleEnum, User

# ── Configuration ──

COPROPRIETES = [
    {
        "nom": "Les Terrasses du Vieux-Port",
        "adresse": "350 Rue de la Commune Ouest",
        "ville": "Montréal",
        "code_postal": "H2Y 2E2",
        "nombre_unites": 100,
        "numero_syndicat": "SYN-MTL-001",
    },
    {
        "nom": "Résidence Place Laurier",
        "adresse": "2700 Boulevard Laurier",
        "ville": "Québec",
        "code_postal": "G1V 2L8",
        "nombre_unites": 50,
        "numero_syndicat": "SYN-QC-002",
    },
    {
        "nom": "Le Cartier du Plateau",
        "adresse": "4200 Avenue du Parc",
        "ville": "Montréal",
        "code_postal": "H2V 4E6",
        "nombre_unites": 10,
        "numero_syndicat": "SYN-MTL-003",
    },
    {
        "nom": "Domaine des Érables",
        "adresse": "155 Chemin du Lac",
        "ville": "Sherbrooke",
        "code_postal": "J1L 1C5",
        "nombre_unites": 5,
        "numero_syndicat": "SYN-SHR-004",
    },
    {
        "nom": "Tours de la Capitale",
        "adresse": "900 Boulevard René-Lévesque Est",
        "ville": "Québec",
        "code_postal": "G1R 2B5",
        "nombre_unites": 1000,
        "numero_syndicat": "SYN-QC-005",
    },
    {
        "nom": "Condos du Fleuve",
        "adresse": "600 Rue de la Rive",
        "ville": "Lévis",
        "code_postal": "G6V 6N2",
        "nombre_unites": 24,
        "numero_syndicat": "SYN-LEV-006",
    },
    {
        "nom": "Place Montcalm",
        "adresse": "1040 Avenue Cartier",
        "ville": "Québec",
        "code_postal": "G1R 2S7",
        "nombre_unites": 36,
        "numero_syndicat": "SYN-QC-007",
    },
    {
        "nom": "Le Saint-Laurent",
        "adresse": "200 Rue Saint-Paul Est",
        "ville": "Montréal",
        "code_postal": "H2Y 1G8",
        "nombre_unites": 80,
        "numero_syndicat": "SYN-MTL-008",
    },
    {
        "nom": "Résidence du Parc Lafontaine",
        "adresse": "1500 Rue Sherbrooke Est",
        "ville": "Montréal",
        "code_postal": "H2L 1M3",
        "nombre_unites": 15,
        "numero_syndicat": "SYN-MTL-009",
    },
    {
        "nom": "Les Jardins de la Rivière",
        "adresse": "85 Boulevard Sainte-Rose",
        "ville": "Laval",
        "code_postal": "H7L 2K8",
        "nombre_unites": 42,
        "numero_syndicat": "SYN-LVL-010",
    },
    {
        "nom": "Manoir Belle-Rive",
        "adresse": "300 Chemin du Bord-de-l'Eau",
        "ville": "Repentigny",
        "code_postal": "J6A 1C3",
        "nombre_unites": 8,
        "numero_syndicat": "SYN-REP-011",
    },
    {
        "nom": "Condos Promenade Champlain",
        "adresse": "2828 Boulevard Champlain",
        "ville": "Québec",
        "code_postal": "G1K 0A1",
        "nombre_unites": 60,
        "numero_syndicat": "SYN-QC-012",
    },
    {
        "nom": "Les Résidences du Canal",
        "adresse": "4500 Rue Saint-Patrick",
        "ville": "Montréal",
        "code_postal": "H4E 1A5",
        "nombre_unites": 120,
        "numero_syndicat": "SYN-MTL-013",
    },
    {
        "nom": "Place de la Cité",
        "adresse": "2590 Boulevard Laurier",
        "ville": "Québec",
        "code_postal": "G1V 4M6",
        "nombre_unites": 200,
        "numero_syndicat": "SYN-QC-014",
    },
    {
        "nom": "Le Boisé de Sainte-Foy",
        "adresse": "3100 Chemin des Quatre-Bourgeois",
        "ville": "Québec",
        "code_postal": "G1W 2K5",
        "nombre_unites": 18,
        "numero_syndicat": "SYN-QC-015",
    },
]

PRENOMS = [
    "Jean", "Marie", "Pierre", "Sophie", "Luc", "Isabelle", "Marc", "Julie",
    "André", "Nathalie", "François", "Caroline", "Martin", "Sylvie", "Daniel",
    "Chantal", "Michel", "Louise", "Robert", "Diane", "Claude", "Hélène",
    "Yves", "Monique", "Alain", "Brigitte", "Jacques", "Josée", "Guy", "Lucie",
]

NOMS = [
    "Tremblay", "Gagnon", "Roy", "Côté", "Bouchard", "Gauthier", "Morin",
    "Lavoie", "Fortin", "Gagné", "Ouellet", "Pelletier", "Bélanger", "Lévesque",
    "Bergeron", "Leblanc", "Paquette", "Girard", "Simard", "Boucher",
    "Caron", "Beaulieu", "Cloutier", "Dubé", "Poirier", "Fournier",
    "Lapointe", "Leclerc", "Lefebvre", "Nadeau",
]

COMPOSANTES_TEMPLATES = [
    ("Membrane de toiture", "toiture", 25, 120000),
    ("Système de chauffage central", "mecanique", 20, 85000),
    ("Ascenseur principal", "ascenseur", 30, 250000),
    ("Revêtement extérieur (briques)", "enveloppe", 50, 200000),
    ("Fenêtres et portes-fenêtres", "enveloppe", 25, 150000),
    ("Plomberie principale", "plomberie", 40, 95000),
    ("Système électrique", "electrique", 35, 70000),
    ("Stationnement souterrain", "stationnement", 40, 300000),
    ("Balcons et garde-corps", "structure", 30, 180000),
    ("Fondation", "structure", 75, 500000),
    ("Système de ventilation", "mecanique", 20, 60000),
    ("Aménagement paysager", "amenagement", 15, 25000),
]

DEPENSES_TEMPLATES = [
    ("Déneigement hiver 2025-2026", "entretien", 4500, "Déneigement Québec Inc."),
    ("Assurance habitation collective", "assurance", 18000, "Desjardins Assurances"),
    ("Hydro-Québec - parties communes", "energie", 3200, "Hydro-Québec"),
    ("Entretien ménager mensuel", "entretien", 1800, "Services Pro-Net"),
    ("Comptabilité et audit annuel", "professionnel", 5500, "Raymond Chabot"),
    ("Réparation ascenseur", "entretien", 3800, "ThyssenKrupp Elevator"),
    ("Inspection bâtiment Loi 16", "professionnel", 7500, "Genispec Inc."),
    ("Peinture corridor 3e étage", "entretien", 2200, "Peinture Excellence"),
    ("Gaz naturel - chauffage", "energie", 6800, "Énergir"),
    ("Frais juridiques - mise en demeure", "professionnel", 1500, "Notaire Lavoie"),
]

MAINTENANCE_TEMPLATES = [
    ("Fuite d'eau salle de bain", "Infiltration d'eau au plafond du 2e étage, provenant de l'unité 305.", "haute"),
    ("Lumière brûlée corridor", "Ampoule du corridor du 4e étage ne fonctionne plus depuis 2 jours.", "basse"),
    ("Bruit dans la tuyauterie", "Bruit anormal quand on ouvre l'eau chaude, possiblement coup de bélier.", "normale"),
    ("Porte du garage ne ferme pas", "La porte automatique du garage P1 reste ouverte depuis ce matin.", "urgente"),
    ("Moisissure salle de bain commune", "Présence de moisissure noire dans la salle de bain du sous-sol.", "haute"),
    ("Interphone défectueux", "L'interphone de l'entrée principale ne sonne plus aux unités.", "normale"),
]

ANNONCES_TEMPLATES = [
    ("Travaux de déneigement", "Les travaux de déneigement du stationnement auront lieu ce samedi à 7h. Veuillez déplacer vos véhicules avant vendredi soir.", False),
    ("Assemblée générale annuelle", "L'assemblée générale annuelle aura lieu le 15 mai 2026 à 19h dans la salle communautaire. Votre présence est importante.", True),
    ("Fermeture piscine pour entretien", "La piscine sera fermée du 1er au 5 avril pour entretien annuel. Merci de votre compréhension.", False),
    ("Rappel - Recyclage", "Rappel : les bacs de recyclage doivent être sortis le mercredi soir, pas le jeudi matin.", False),
    ("Nouveau règlement - Animaux", "Le CA a adopté une modification au règlement concernant les animaux domestiques. Consultez le document dans la section Documents.", True),
]


def now():
    return datetime.now(timezone.utc)


def seed_database():
    engine = create_engine(DATABASE_URL, echo=False)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Vérifier si le seed a déjà été appliqué (via admin@syndipro.qc)
        admin_exists = session.exec(
            select(User).where(User.email == "admin@syndipro.qc")
        ).first()
        if admin_exists:
            print("Le compte admin@syndipro.qc existe déjà. Seed déjà appliqué.")
            print("Les comptes de test sont disponibles — voir la liste ci-dessous.")
            return

        print("Création des données de test (préservation des utilisateurs existants)...")

        # ── 1. Utilisateurs ──
        users = []
        admin = User(
            email="admin@syndipro.qc",
            nom="Administrateur",
            prenom="SyndiPro",
            hashed_password=hash_password("Admin123!"),
            role=RoleEnum.gestionnaire,
        )
        session.add(admin)
        users.append(admin)

        for i in range(30):
            prenom = PRENOMS[i % len(PRENOMS)]
            nom = NOMS[i % len(NOMS)]
            user = User(
                email=f"{prenom.lower()}.{nom.lower()}{i}@exemple.qc",
                nom=nom,
                prenom=prenom,
                hashed_password=hash_password("Test123!"),
                role=random.choice([RoleEnum.admin_ca, RoleEnum.coproprietaire]),
            )
            session.add(user)
            users.append(user)

        session.flush()
        print(f"  {len(users)} utilisateurs créés")

        # ── 2. Syndicats + Membres + Unités ──
        syndicats = []
        for copro_data in COPROPRIETES:
            syndicat = Syndicat(**copro_data)
            session.add(syndicat)
            session.flush()
            syndicats.append(syndicat)

            # Add members (president + random members)
            membre_count = min(copro_data["nombre_unites"], 8)
            assigned_users = random.sample(users[1:], min(membre_count, len(users) - 1))
            roles = [RoleSyndicat.president, RoleSyndicat.tresorier, RoleSyndicat.secretaire]

            for j, user in enumerate(assigned_users):
                role = roles[j] if j < len(roles) else RoleSyndicat.coproprietaire
                membre = MembreSyndicat(
                    user_id=user.id,
                    syndicat_id=syndicat.id,
                    role_syndicat=role,
                )
                session.add(membre)

            # Also add admin to all syndicats
            admin_membre = MembreSyndicat(
                user_id=admin.id,
                syndicat_id=syndicat.id,
                role_syndicat=RoleSyndicat.administrateur,
            )
            session.add(admin_membre)

            # Create units (cap at 50 for very large buildings)
            unit_count = min(copro_data["nombre_unites"], 50)
            for k in range(unit_count):
                etage = (k // 4) + 1
                numero = f"{etage}{(k % 4) + 1:02d}"
                unite = Unite(
                    syndicat_id=syndicat.id,
                    numero=numero,
                    etage=etage,
                    superficie_m2=round(random.uniform(45, 120), 1),
                    quote_part=round(100 / copro_data["nombre_unites"], 2),
                    proprietaire_id=assigned_users[k % len(assigned_users)].id
                    if k < len(assigned_users) * 3
                    else None,
                )
                session.add(unite)

        session.flush()
        print(f"  {len(syndicats)} syndicats créés avec membres et unités")

        # ── 3. Finances ──
        for syndicat in syndicats:
            # Dépenses
            num_depenses = random.randint(3, 8)
            templates = random.sample(DEPENSES_TEMPLATES, min(num_depenses, len(DEPENSES_TEMPLATES)))
            for desc, cat, montant, fournisseur in templates:
                scale = syndicat.nombre_unites / 24
                depense = Depense(
                    syndicat_id=syndicat.id,
                    description=desc,
                    montant=round(montant * scale, 2),
                    categorie=cat,
                    date_depense=date.today() - timedelta(days=random.randint(1, 180)),
                    fournisseur=fournisseur,
                )
                session.add(depense)

            # Cotisations for first few units
            unites = list(session.exec(
                select(Unite).where(Unite.syndicat_id == syndicat.id).limit(10)
            ).all())
            for unite in unites[:5]:
                for mois in range(1, 5):
                    cotisation = Cotisation(
                        syndicat_id=syndicat.id,
                        unite_id=unite.id,
                        montant=round(random.uniform(250, 600), 2),
                        mois=mois,
                        annee=2026,
                        date_echeance=date(2026, mois, 1),
                        statut=random.choice(["payee", "payee", "payee", "en_attente", "en_retard"]),
                        date_paiement=date(2026, mois, random.randint(1, 15))
                        if random.random() > 0.3
                        else None,
                    )
                    session.add(cotisation)

            # Fonds de prévoyance
            fonds = FondsPrevoyance(
                syndicat_id=syndicat.id,
                solde_actuel=round(random.uniform(20000, 500000) * (syndicat.nombre_unites / 24), 2),
                contribution_mensuelle=round(random.uniform(500, 5000) * (syndicat.nombre_unites / 24), 2),
                objectif_25_ans=round(random.uniform(500000, 2000000) * (syndicat.nombre_unites / 24), 2),
                derniere_etude=date.today() - timedelta(days=random.randint(30, 1800)),
                prochaine_etude=date.today() + timedelta(days=random.randint(365, 1825)),
            )
            session.add(fonds)

        session.flush()
        print("  Données financières créées (cotisations, dépenses, fonds)")

        # ── 4. Assemblées & Votes ──
        for syndicat in syndicats[:8]:
            assemblee = Assemblee(
                syndicat_id=syndicat.id,
                titre=f"Assemblée générale annuelle 2026 - {syndicat.nom}",
                description="Ordre du jour : Budget, travaux majeurs, élection du CA.",
                type_assemblee="annuelle",
                date_assemblee=datetime(2026, 5, 15, 19, 0, tzinfo=timezone.utc),
                lieu="Salle communautaire",
                statut="planifiee",
                quorum_requis=50.0,
            )
            session.add(assemblee)
            session.flush()

            resolutions_data = [
                ("Adoption du budget 2026-2027", "Budget annuel de fonctionnement et fonds de prévoyance.", 1),
                ("Approbation des états financiers 2025", "Présentation et approbation des états financiers vérifiés.", 2),
                ("Travaux de toiture - phase 2", "Autorisation des travaux de réfection de la toiture estimés à 120 000$.", 3),
            ]
            for titre, desc, ordre in resolutions_data:
                resolution = Resolution(
                    assemblee_id=assemblee.id,
                    titre=titre,
                    description=desc,
                    ordre=ordre,
                )
                session.add(resolution)

        session.flush()
        print("  Assemblées et résolutions créées")

        # ── 5. Maintenance ──
        for syndicat in syndicats:
            num_demandes = random.randint(1, 4)
            templates = random.sample(MAINTENANCE_TEMPLATES, min(num_demandes, len(MAINTENANCE_TEMPLATES)))
            membres = list(session.exec(
                select(MembreSyndicat).where(MembreSyndicat.syndicat_id == syndicat.id).limit(3)
            ).all())
            for titre, desc, urgence in templates:
                demandeur = random.choice(membres) if membres else None
                demande = DemandeMaintenance(
                    syndicat_id=syndicat.id,
                    demandeur_id=demandeur.user_id if demandeur else admin.id,
                    titre=titre,
                    description=desc,
                    urgence=urgence,
                    statut=random.choice(["soumise", "en_cours", "assignee", "completee"]),
                )
                session.add(demande)

        session.flush()
        print("  Demandes de maintenance créées")

        # ── 6. Documents ──
        doc_templates = [
            ("Procès-verbal AG 2025", "proces-verbal"),
            ("Règlement d'immeuble", "reglement"),
            ("Police d'assurance 2026", "assurance"),
            ("Budget prévisionnel 2026", "financier"),
            ("Contrat de déneigement", "contrat"),
            ("Déclaration de copropriété", "reglement"),
        ]
        for syndicat in syndicats:
            for nom, cat in random.sample(doc_templates, random.randint(2, 5)):
                doc = Document(
                    syndicat_id=syndicat.id,
                    uploaded_by_id=admin.id,
                    nom=f"{nom} - {syndicat.nom[:20]}",
                    categorie=cat,
                    description=f"Document officiel du syndicat",
                )
                session.add(doc)

        session.flush()
        print("  Documents créés")

        # ── 7. Annonces ──
        for syndicat in syndicats[:10]:
            for titre, contenu, epingle in random.sample(ANNONCES_TEMPLATES, random.randint(1, 3)):
                annonce = Annonce(
                    syndicat_id=syndicat.id,
                    auteur_id=admin.id,
                    titre=titre,
                    contenu=contenu,
                    est_epinglee=epingle,
                )
                session.add(annonce)

        session.flush()
        print("  Annonces créées")

        # ── 8. Composantes Loi 16 ──
        for syndicat in syndicats:
            num_composantes = random.randint(4, len(COMPOSANTES_TEMPLATES))
            templates = random.sample(COMPOSANTES_TEMPLATES, num_composantes)
            for nom, cat, duree_vie, cout in templates:
                annee = random.randint(1990, 2020)
                etat = random.choice(["bon", "bon", "acceptable", "a_surveiller", "a_remplacer"])
                composante = ComposanteImmeuble(
                    syndicat_id=syndicat.id,
                    nom=nom,
                    categorie=cat,
                    annee_installation=annee,
                    duree_vie_estimee=duree_vie,
                    etat=etat,
                    cout_remplacement_estime=round(cout * (syndicat.nombre_unites / 24), 2),
                    derniere_inspection=date.today() - timedelta(days=random.randint(30, 730))
                    if random.random() > 0.3
                    else None,
                    prochaine_inspection=date.today() + timedelta(days=random.randint(90, 730))
                    if random.random() > 0.4
                    else None,
                )
                session.add(composante)
                session.flush()

                # Add carnet entries for some composantes
                if random.random() > 0.4:
                    entree = EntreeCarnet(
                        composante_id=composante.id,
                        syndicat_id=syndicat.id,
                        type_intervention=random.choice(["inspection", "reparation", "entretien"]),
                        description=f"Intervention sur {nom} - rapport satisfaisant",
                        date_intervention=date.today() - timedelta(days=random.randint(30, 365)),
                        cout=round(random.uniform(500, 15000), 2) if random.random() > 0.5 else None,
                        effectue_par=random.choice(["Genispec Inc.", "Inspections Bâtiment QC", "Services Pro-Immeuble"]),
                    )
                    session.add(entree)

        session.flush()
        print("  Composantes Loi 16 et carnet d'entretien créés")

        # ── Commit ──
        session.commit()

        # ── Summary ──
        user_count = len(list(session.exec(select(User)).all()))
        syndicat_count = len(list(session.exec(select(Syndicat)).all()))
        unite_count = len(list(session.exec(select(Unite)).all()))
        membre_count = len(list(session.exec(select(MembreSyndicat)).all()))
        cotisation_count = len(list(session.exec(select(Cotisation)).all()))
        depense_count = len(list(session.exec(select(Depense)).all()))
        assemblee_count = len(list(session.exec(select(Assemblee)).all()))
        demande_count = len(list(session.exec(select(DemandeMaintenance)).all()))
        doc_count = len(list(session.exec(select(Document)).all()))
        annonce_count = len(list(session.exec(select(Annonce)).all()))
        composante_count = len(list(session.exec(select(ComposanteImmeuble)).all()))
        entree_count = len(list(session.exec(select(EntreeCarnet)).all()))

        print("\n" + "=" * 50)
        print("SEED DATA TERMINÉ")
        print("=" * 50)
        print(f"  Utilisateurs     : {user_count}")
        print(f"  Syndicats        : {syndicat_count}")
        print(f"  Unités           : {unite_count}")
        print(f"  Membres          : {membre_count}")
        print(f"  Cotisations      : {cotisation_count}")
        print(f"  Dépenses         : {depense_count}")
        print(f"  Fonds prévoyance : {syndicat_count}")
        print(f"  Assemblées       : {assemblee_count}")
        print(f"  Demandes maint.  : {demande_count}")
        print(f"  Documents        : {doc_count}")
        print(f"  Annonces         : {annonce_count}")
        print(f"  Composantes L16  : {composante_count}")
        print(f"  Entrées carnet   : {entree_count}")
        print()
        print("Comptes de test:")
        print("  admin@syndipro.qc / Admin123!  (gestionnaire, accès à tous les syndicats)")
        print("  jean.tremblay0@exemple.qc / Test123!  (copropriétaire)")
        print("=" * 50)


if __name__ == "__main__":
    seed_database()
