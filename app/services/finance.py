import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.finance import (
    Cotisation,
    Depense,
    FondsPrevoyance,
    StatutCotisation,
)
from app.models.syndicat import Syndicat
from app.schemas.finance import (
    BilanFinancier,
    CotisationCreate,
    CotisationUpdate,
    DepenseCreate,
    DepenseUpdate,
    FondsPrevoyanceCreate,
    FondsPrevoyanceUpdate,
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


# ── Cotisations ─────────────────────────────────────────────────────


def create_cotisation(
    syndicat_id: uuid.UUID, data: CotisationCreate, session: Session
) -> Cotisation:
    """Crée une nouvelle cotisation pour une unité"""
    _check_syndicat(syndicat_id, session)

    cotisation = Cotisation(syndicat_id=syndicat_id, **data.model_dump())
    session.add(cotisation)
    session.commit()
    session.refresh(cotisation)
    return cotisation


def get_cotisations_by_syndicat(
    syndicat_id: uuid.UUID,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Cotisation]:
    """Retourne les cotisations d'un syndicat"""
    return list(
        session.exec(
            select(Cotisation)
            .where(Cotisation.syndicat_id == syndicat_id)
            .offset(skip)
            .limit(limit)
        ).all()
    )


def update_cotisation(
    cotisation_id: uuid.UUID, data: CotisationUpdate, session: Session
) -> Cotisation:
    """Met à jour une cotisation (statut, paiement, montant)"""
    cotisation = session.get(Cotisation, cotisation_id)
    if not cotisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cotisation non trouvée",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cotisation, key, value)

    session.add(cotisation)
    session.commit()
    session.refresh(cotisation)
    return cotisation


# ── Dépenses ────────────────────────────────────────────────────────


def create_depense(syndicat_id: uuid.UUID, data: DepenseCreate, session: Session) -> Depense:
    """Crée une nouvelle dépense pour un syndicat"""
    _check_syndicat(syndicat_id, session)

    depense = Depense(syndicat_id=syndicat_id, **data.model_dump())
    session.add(depense)
    session.commit()
    session.refresh(depense)
    return depense


def get_depenses_by_syndicat(
    syndicat_id: uuid.UUID,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Depense]:
    """Retourne les dépenses d'un syndicat"""
    return list(
        session.exec(
            select(Depense).where(Depense.syndicat_id == syndicat_id).offset(skip).limit(limit)
        ).all()
    )


def update_depense(depense_id: uuid.UUID, data: DepenseUpdate, session: Session) -> Depense:
    """Met à jour une dépense existante"""
    depense = session.get(Depense, depense_id)
    if not depense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dépense non trouvée",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(depense, key, value)

    session.add(depense)
    session.commit()
    session.refresh(depense)
    return depense


# ── Fonds de prévoyance ─────────────────────────────────────────────


def create_fonds_prevoyance(
    syndicat_id: uuid.UUID, data: FondsPrevoyanceCreate, session: Session
) -> FondsPrevoyance:
    """Crée le fonds de prévoyance d'un syndicat"""
    _check_syndicat(syndicat_id, session)

    # Un seul fonds par syndicat
    existing = session.exec(
        select(FondsPrevoyance).where(FondsPrevoyance.syndicat_id == syndicat_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce syndicat a déjà un fonds de prévoyance",
        )

    fonds = FondsPrevoyance(syndicat_id=syndicat_id, **data.model_dump())
    session.add(fonds)
    session.commit()
    session.refresh(fonds)
    return fonds


def get_fonds_prevoyance(syndicat_id: uuid.UUID, session: Session) -> FondsPrevoyance:
    """Retourne le fonds de prévoyance d'un syndicat"""
    fonds = session.exec(
        select(FondsPrevoyance).where(FondsPrevoyance.syndicat_id == syndicat_id)
    ).first()
    if not fonds:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fonds de prévoyance non trouvé",
        )
    return fonds


def update_fonds_prevoyance(
    syndicat_id: uuid.UUID, data: FondsPrevoyanceUpdate, session: Session
) -> FondsPrevoyance:
    """Met à jour le fonds de prévoyance d'un syndicat"""
    fonds = get_fonds_prevoyance(syndicat_id, session)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(fonds, key, value)

    fonds.updated_at = datetime.now(timezone.utc)
    session.add(fonds)
    session.commit()
    session.refresh(fonds)
    return fonds


# ── Bilan financier ─────────────────────────────────────────────────


def get_bilan_financier(syndicat_id: uuid.UUID, session: Session) -> BilanFinancier:
    """Calcule le bilan financier d'un syndicat"""
    _check_syndicat(syndicat_id, session)

    # Toutes les cotisations du syndicat
    cotisations = list(
        session.exec(select(Cotisation).where(Cotisation.syndicat_id == syndicat_id)).all()
    )

    total_attendues = sum(c.montant for c in cotisations)
    total_recues = sum(c.montant for c in cotisations if c.statut == StatutCotisation.payee)
    en_retard = sum(1 for c in cotisations if c.statut == StatutCotisation.en_retard)
    en_attente = sum(1 for c in cotisations if c.statut == StatutCotisation.en_attente)

    # Toutes les dépenses du syndicat
    depenses = list(session.exec(select(Depense).where(Depense.syndicat_id == syndicat_id)).all())
    total_depenses = sum(d.montant for d in depenses)

    # Fonds de prévoyance
    fonds = session.exec(
        select(FondsPrevoyance).where(FondsPrevoyance.syndicat_id == syndicat_id)
    ).first()
    fonds_solde = fonds.solde_actuel if fonds else None

    return BilanFinancier(
        syndicat_id=syndicat_id,
        total_cotisations_attendues=total_attendues,
        total_cotisations_recues=total_recues,
        total_depenses=total_depenses,
        solde=total_recues - total_depenses,
        cotisations_en_retard=en_retard,
        cotisations_en_attente=en_attente,
        fonds_prevoyance_solde=fonds_solde,
    )
