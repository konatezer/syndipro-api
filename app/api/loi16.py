import uuid

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.models.user import User
from app.schemas.loi16 import (
    ComposanteImmeubleCreate,
    ComposanteImmeubleResponse,
    ComposanteImmeubleUpdate,
    EntreeCarnetCreate,
    EntreeCarnetResponse,
    ScoreConformiteDetail,
    ScoreConformiteResponse,
)
from app.services.auth import get_current_user
from app.services.loi16 import (
    calculate_score_conformite,
    create_composante,
    create_entree_carnet,
    get_composantes_by_syndicat,
    get_composantes_critiques,
    get_entrees_by_syndicat,
    get_or_create_score,
    update_composante,
)

router = APIRouter(tags=["Loi 16 — Conformité"])


# ── Composantes d'immeuble ────────────────────────────────────────


@router.post(
    "/syndicats/{syndicat_id}/composantes",
    response_model=ComposanteImmeubleResponse,
    status_code=201,
)
def create_composante_route(
    syndicat_id: uuid.UUID,
    data: ComposanteImmeubleCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Créer une composante d'immeuble pour le carnet d'entretien"""
    return create_composante(syndicat_id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/composantes",
    response_model=list[ComposanteImmeubleResponse],
)
def list_composantes(
    syndicat_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les composantes d'immeuble d'un syndicat"""
    return get_composantes_by_syndicat(syndicat_id, session, skip, limit)


@router.put(
    "/composantes/{composante_id}",
    response_model=ComposanteImmeubleResponse,
)
def update_composante_route(
    composante_id: uuid.UUID,
    data: ComposanteImmeubleUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Modifier une composante d'immeuble"""
    return update_composante(composante_id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/composantes/critiques",
    response_model=list[ComposanteImmeubleResponse],
)
def list_composantes_critiques(
    syndicat_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les composantes en état critique, à remplacer ou à surveiller"""
    return get_composantes_critiques(syndicat_id, session)


# ── Carnet d'entretien ────────────────────────────────────────────


@router.post(
    "/syndicats/{syndicat_id}/carnet",
    response_model=EntreeCarnetResponse,
    status_code=201,
)
def create_entree_carnet_route(
    syndicat_id: uuid.UUID,
    data: EntreeCarnetCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Créer une entrée dans le carnet d'entretien"""
    return create_entree_carnet(syndicat_id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/carnet",
    response_model=list[EntreeCarnetResponse],
)
def list_entrees_carnet(
    syndicat_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les entrées du carnet d'entretien d'un syndicat"""
    return get_entrees_by_syndicat(syndicat_id, session, skip, limit)


# ── Score de conformité ───────────────────────────────────────────


@router.get(
    "/syndicats/{syndicat_id}/conformite",
    response_model=ScoreConformiteDetail,
)
def get_conformite(
    syndicat_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Obtenir le score de conformité Loi 16 d'un syndicat"""
    score = get_or_create_score(syndicat_id, session)
    composantes = get_composantes_by_syndicat(syndicat_id, session)
    entrees = get_entrees_by_syndicat(syndicat_id, session)
    critiques = get_composantes_critiques(syndicat_id, session)

    return ScoreConformiteDetail(
        score=ScoreConformiteResponse.model_validate(score),
        nombre_composantes=len(composantes),
        nombre_entrees_carnet=len(entrees),
        composantes_critiques=len(critiques),
    )


@router.post(
    "/syndicats/{syndicat_id}/conformite/evaluer",
    response_model=ScoreConformiteDetail,
)
def evaluer_conformite(
    syndicat_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Recalculer le score de conformité Loi 16 d'un syndicat"""
    score = calculate_score_conformite(syndicat_id, session)
    composantes = get_composantes_by_syndicat(syndicat_id, session)
    entrees = get_entrees_by_syndicat(syndicat_id, session)
    critiques = get_composantes_critiques(syndicat_id, session)

    return ScoreConformiteDetail(
        score=ScoreConformiteResponse.model_validate(score),
        nombre_composantes=len(composantes),
        nombre_entrees_carnet=len(entrees),
        composantes_critiques=len(critiques),
    )
