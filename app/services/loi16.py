import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.finance import FondsPrevoyance
from app.models.loi16 import (
    ComposanteImmeuble,
    EntreeCarnet,
    EtatComposante,
    ScoreConformite,
)
from app.models.syndicat import Syndicat
from app.schemas.loi16 import (
    ComposanteImmeubleCreate,
    ComposanteImmeubleUpdate,
    EntreeCarnetCreate,
)

# ── Helpers ─────────────────────────────────────────────────────────


def _check_syndicat(syndicat_id: uuid.UUID, session: Session) -> Syndicat:
    """Vérifie qu'un syndicat existe et est actif"""
    syndicat = session.get(Syndicat, syndicat_id)
    if not syndicat or not syndicat.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Syndicat non trouvé",
        )
    return syndicat


# ── Composantes d'immeuble ────────────────────────────────────────


def create_composante(
    syndicat_id: uuid.UUID,
    data: ComposanteImmeubleCreate,
    session: Session,
) -> ComposanteImmeuble:
    """Crée une nouvelle composante d'immeuble"""
    _check_syndicat(syndicat_id, session)

    composante = ComposanteImmeuble(
        syndicat_id=syndicat_id,
        **data.model_dump(),
    )
    session.add(composante)
    session.commit()
    session.refresh(composante)
    return composante


def get_composantes_by_syndicat(
    syndicat_id: uuid.UUID,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[ComposanteImmeuble]:
    """Retourne les composantes d'immeuble d'un syndicat"""
    return list(
        session.exec(
            select(ComposanteImmeuble)
            .where(ComposanteImmeuble.syndicat_id == syndicat_id)
            .offset(skip)
            .limit(limit)
        ).all()
    )


def update_composante(
    composante_id: uuid.UUID,
    data: ComposanteImmeubleUpdate,
    session: Session,
) -> ComposanteImmeuble:
    """Met à jour une composante d'immeuble"""
    composante = session.get(ComposanteImmeuble, composante_id)
    if not composante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Composante non trouvée",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(composante, key, value)

    session.add(composante)
    session.commit()
    session.refresh(composante)
    return composante


def get_composantes_critiques(
    syndicat_id: uuid.UUID,
    session: Session,
) -> list[ComposanteImmeuble]:
    """Retourne les composantes en état critique, à remplacer ou à surveiller"""
    etats_critiques = [
        EtatComposante.a_surveiller,
        EtatComposante.a_remplacer,
        EtatComposante.critique,
    ]
    return list(
        session.exec(
            select(ComposanteImmeuble).where(
                ComposanteImmeuble.syndicat_id == syndicat_id,
                ComposanteImmeuble.etat.in_(etats_critiques),
            )
        ).all()
    )


# ── Entrées du carnet d'entretien ─────────────────────────────────


def create_entree_carnet(
    syndicat_id: uuid.UUID,
    data: EntreeCarnetCreate,
    session: Session,
) -> EntreeCarnet:
    """Crée une nouvelle entrée dans le carnet d'entretien"""
    _check_syndicat(syndicat_id, session)

    # Vérifier que la composante existe et appartient au syndicat
    composante = session.get(ComposanteImmeuble, data.composante_id)
    if not composante or composante.syndicat_id != syndicat_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Composante non trouvée pour ce syndicat",
        )

    entree = EntreeCarnet(
        syndicat_id=syndicat_id,
        **data.model_dump(),
    )
    session.add(entree)
    session.commit()
    session.refresh(entree)
    return entree


def get_entrees_by_syndicat(
    syndicat_id: uuid.UUID,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[EntreeCarnet]:
    """Retourne les entrées du carnet d'entretien d'un syndicat"""
    return list(
        session.exec(
            select(EntreeCarnet)
            .where(EntreeCarnet.syndicat_id == syndicat_id)
            .offset(skip)
            .limit(limit)
        ).all()
    )


# ── Score de conformité ───────────────────────────────────────────


def get_or_create_score(
    syndicat_id: uuid.UUID,
    session: Session,
) -> ScoreConformite:
    """Retourne le score de conformité d'un syndicat, ou en crée un vide"""
    _check_syndicat(syndicat_id, session)

    score = session.exec(
        select(ScoreConformite).where(ScoreConformite.syndicat_id == syndicat_id)
    ).first()

    if not score:
        score = ScoreConformite(syndicat_id=syndicat_id)
        session.add(score)
        session.commit()
        session.refresh(score)

    return score


def calculate_score_conformite(
    syndicat_id: uuid.UUID,
    session: Session,
) -> ScoreConformite:
    """Calcule le score de conformité Loi 16 basé sur 5 critères de 20 points chacun.

    - 20 pts: A des composantes enregistrées (carnet d'entretien)
    - 20 pts: A des entrées récentes dans le carnet (moins de 2 ans)
    - 20 pts: Fonds de prévoyance existe
    - 20 pts: Étude du fonds à jour (dernière étude < 5 ans)
    - 20 pts: Couverture > 80% des composantes ont été inspectées
    """
    _check_syndicat(syndicat_id, session)

    score_global = 0.0
    recommandations_list: list[str] = []

    # Critère 1 : A des composantes enregistrées (20 pts)
    composantes = list(
        session.exec(
            select(ComposanteImmeuble).where(ComposanteImmeuble.syndicat_id == syndicat_id)
        ).all()
    )
    carnet_entretien_ok = len(composantes) > 0
    if carnet_entretien_ok:
        score_global += 20
    else:
        recommandations_list.append(
            "Enregistrer les composantes de l'immeuble dans le carnet d'entretien."
        )

    # Critère 2 : A des entrées récentes (20 pts)
    today = date.today()
    two_years_ago = today.replace(year=today.year - 2)
    entrees_recentes = list(
        session.exec(
            select(EntreeCarnet).where(
                EntreeCarnet.syndicat_id == syndicat_id,
                EntreeCarnet.date_intervention >= two_years_ago,
            )
        ).all()
    )
    has_recent_entrees = len(entrees_recentes) > 0
    if has_recent_entrees:
        score_global += 20
    else:
        recommandations_list.append(
            "Ajouter des entrées récentes au carnet d'entretien "
            "(inspections, réparations, entretien)."
        )

    # Critère 3 : Fonds de prévoyance existe (20 pts)
    fonds = session.exec(
        select(FondsPrevoyance).where(FondsPrevoyance.syndicat_id == syndicat_id)
    ).first()
    fonds_prevoyance_ok = fonds is not None
    if fonds_prevoyance_ok:
        score_global += 20
    else:
        recommandations_list.append("Créer un fonds de prévoyance pour le syndicat.")

    # Critère 4 : Étude du fonds à jour (20 pts)
    etude_fonds_a_jour = False
    if fonds and fonds.derniere_etude:
        five_years_ago = today.replace(year=today.year - 5)
        etude_fonds_a_jour = fonds.derniere_etude >= five_years_ago
    if etude_fonds_a_jour:
        score_global += 20
    else:
        recommandations_list.append(
            "Réaliser ou mettre à jour l'étude du fonds de prévoyance (obligatoire tous les 5 ans)."
        )

    # Critère 5 : Couverture > 80% (20 pts)
    attestation_disponible = False
    if len(composantes) > 0:
        composantes_inspectees = sum(1 for c in composantes if c.derniere_inspection is not None)
        couverture = composantes_inspectees / len(composantes)
        attestation_disponible = couverture > 0.80
    if attestation_disponible:
        score_global += 20
    else:
        recommandations_list.append(
            "Inspecter au moins 80% des composantes pour obtenir l'attestation de conformité."
        )

    # Construire les recommandations en texte
    recommandations = "; ".join(recommandations_list) if recommandations_list else None

    # Mettre à jour ou créer le score
    score = session.exec(
        select(ScoreConformite).where(ScoreConformite.syndicat_id == syndicat_id)
    ).first()

    now = datetime.now(timezone.utc)

    if score:
        score.score_global = score_global
        score.carnet_entretien_ok = carnet_entretien_ok
        score.fonds_prevoyance_ok = fonds_prevoyance_ok
        score.etude_fonds_a_jour = etude_fonds_a_jour
        score.attestation_disponible = attestation_disponible
        score.derniere_evaluation = now
        score.recommandations = recommandations
        score.updated_at = now
    else:
        score = ScoreConformite(
            syndicat_id=syndicat_id,
            score_global=score_global,
            carnet_entretien_ok=carnet_entretien_ok,
            fonds_prevoyance_ok=fonds_prevoyance_ok,
            etude_fonds_a_jour=etude_fonds_a_jour,
            attestation_disponible=attestation_disponible,
            derniere_evaluation=now,
            recommandations=recommandations,
        )
        session.add(score)

    session.commit()
    session.refresh(score)
    return score
