import uuid

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.models.user import User
from app.schemas.finance import (
    BilanFinancier,
    CotisationCreate,
    CotisationResponse,
    CotisationUpdate,
    DepenseCreate,
    DepenseResponse,
    DepenseUpdate,
    FondsPrevoyanceCreate,
    FondsPrevoyanceResponse,
    FondsPrevoyanceUpdate,
)
from app.services.auth import get_current_user
from app.services.finance import (
    create_cotisation,
    create_depense,
    create_fonds_prevoyance,
    get_bilan_financier,
    get_cotisations_by_syndicat,
    get_depenses_by_syndicat,
    get_fonds_prevoyance,
    update_cotisation,
    update_depense,
    update_fonds_prevoyance,
)

router = APIRouter(tags=["Finances"])


# ── Cotisations ─────────────────────────────────────────────────────


@router.post(
    "/syndicats/{syndicat_id}/cotisations",
    response_model=CotisationResponse,
    status_code=201,
)
def create_cotisation_route(
    syndicat_id: uuid.UUID,
    data: CotisationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Créer une cotisation pour une unité du syndicat"""
    return create_cotisation(syndicat_id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/cotisations",
    response_model=list[CotisationResponse],
)
def list_cotisations(
    syndicat_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les cotisations d'un syndicat"""
    return get_cotisations_by_syndicat(syndicat_id, session, skip, limit)


@router.put("/cotisations/{cotisation_id}", response_model=CotisationResponse)
def update_cotisation_route(
    cotisation_id: uuid.UUID,
    data: CotisationUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Modifier une cotisation (statut, paiement)"""
    return update_cotisation(cotisation_id, data, session)


# ── Dépenses ────────────────────────────────────────────────────────


@router.post(
    "/syndicats/{syndicat_id}/depenses",
    response_model=DepenseResponse,
    status_code=201,
)
def create_depense_route(
    syndicat_id: uuid.UUID,
    data: DepenseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Créer une dépense pour un syndicat"""
    return create_depense(syndicat_id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/depenses",
    response_model=list[DepenseResponse],
)
def list_depenses(
    syndicat_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les dépenses d'un syndicat"""
    return get_depenses_by_syndicat(syndicat_id, session, skip, limit)


@router.put("/depenses/{depense_id}", response_model=DepenseResponse)
def update_depense_route(
    depense_id: uuid.UUID,
    data: DepenseUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Modifier une dépense existante"""
    return update_depense(depense_id, data, session)


# ── Fonds de prévoyance ─────────────────────────────────────────────


@router.post(
    "/syndicats/{syndicat_id}/fonds-prevoyance",
    response_model=FondsPrevoyanceResponse,
    status_code=201,
)
def create_fonds_route(
    syndicat_id: uuid.UUID,
    data: FondsPrevoyanceCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Créer le fonds de prévoyance d'un syndicat"""
    return create_fonds_prevoyance(syndicat_id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/fonds-prevoyance",
    response_model=FondsPrevoyanceResponse,
)
def get_fonds_route(
    syndicat_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Obtenir le fonds de prévoyance d'un syndicat"""
    return get_fonds_prevoyance(syndicat_id, session)


@router.put(
    "/syndicats/{syndicat_id}/fonds-prevoyance",
    response_model=FondsPrevoyanceResponse,
)
def update_fonds_route(
    syndicat_id: uuid.UUID,
    data: FondsPrevoyanceUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Modifier le fonds de prévoyance d'un syndicat"""
    return update_fonds_prevoyance(syndicat_id, data, session)


# ── Bilan financier ─────────────────────────────────────────────────


@router.get(
    "/syndicats/{syndicat_id}/bilan",
    response_model=BilanFinancier,
)
def get_bilan(
    syndicat_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Obtenir le bilan financier d'un syndicat"""
    return get_bilan_financier(syndicat_id, session)
