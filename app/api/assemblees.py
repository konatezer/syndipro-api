import uuid

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.models.user import User
from app.schemas.assemblee import (
    AssembleeCreate,
    AssembleeDetailResponse,
    AssembleeResponse,
    AssembleeUpdate,
    ResolutionCreate,
    ResolutionResponse,
    ResultatVote,
    VoteCreate,
    VoteResponse,
)
from app.services.assemblee import (
    add_resolution,
    create_assemblee,
    get_assemblee,
    get_assemblee_detail,
    get_assemblees_by_syndicat,
    get_resultat_vote,
    submit_vote,
    update_assemblee,
)
from app.services.auth import get_current_user

router = APIRouter(tags=["Assemblées & Votes"])


# ── Assemblées ─────────────────────────────────────────────────────


@router.post(
    "/syndicats/{syndicat_id}/assemblees",
    response_model=AssembleeResponse,
    status_code=201,
)
def create_assemblee_route(
    syndicat_id: uuid.UUID,
    data: AssembleeCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Créer une assemblée pour un syndicat"""
    return create_assemblee(syndicat_id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/assemblees",
    response_model=list[AssembleeResponse],
)
def list_assemblees(
    syndicat_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les assemblées d'un syndicat"""
    return get_assemblees_by_syndicat(syndicat_id, session, skip, limit)


@router.get("/assemblees/{assemblee_id}", response_model=AssembleeResponse)
def get_assemblee_route(
    assemblee_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Obtenir une assemblée par son ID"""
    return get_assemblee(assemblee_id, session)


@router.put("/assemblees/{assemblee_id}", response_model=AssembleeResponse)
def update_assemblee_route(
    assemblee_id: uuid.UUID,
    data: AssembleeUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Modifier une assemblée existante"""
    return update_assemblee(assemblee_id, data, session)


# ── Résolutions ────────────────────────────────────────────────────


@router.post(
    "/assemblees/{assemblee_id}/resolutions",
    response_model=ResolutionResponse,
    status_code=201,
)
def add_resolution_route(
    assemblee_id: uuid.UUID,
    data: ResolutionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Ajouter une résolution à une assemblée"""
    return add_resolution(assemblee_id, data, session)


# ── Votes ──────────────────────────────────────────────────────────


@router.post(
    "/resolutions/{resolution_id}/votes",
    response_model=VoteResponse,
    status_code=201,
)
def submit_vote_route(
    resolution_id: uuid.UUID,
    data: VoteCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Soumettre un vote sur une résolution"""
    return submit_vote(resolution_id, current_user.id, data, session)


@router.get(
    "/resolutions/{resolution_id}/resultats",
    response_model=ResultatVote,
)
def get_resultats_route(
    resolution_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Obtenir les résultats de vote d'une résolution"""
    return get_resultat_vote(resolution_id, session)


# ── Détail assemblée ──────────────────────────────────────────────


@router.get(
    "/assemblees/{assemblee_id}/detail",
    response_model=AssembleeDetailResponse,
)
def get_assemblee_detail_route(
    assemblee_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Obtenir le détail complet d'une assemblée avec résolutions et votes"""
    return get_assemblee_detail(assemblee_id, session)
