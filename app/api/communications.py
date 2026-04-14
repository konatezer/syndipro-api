import uuid

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.models.user import User
from app.schemas.communication import (
    AnnonceCreate,
    AnnonceResponse,
    AnnonceUpdate,
)
from app.services.auth import get_current_user
from app.services.communication import (
    create_annonce,
    delete_annonce,
    get_annonces_by_syndicat,
    update_annonce,
)

router = APIRouter(tags=["Communications"])


# ── Annonces ───────────────────────────────────────────────────────


@router.post(
    "/syndicats/{syndicat_id}/annonces",
    response_model=AnnonceResponse,
    status_code=201,
)
def create_annonce_route(
    syndicat_id: uuid.UUID,
    data: AnnonceCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Créer une annonce pour un syndicat"""
    return create_annonce(syndicat_id, current_user.id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/annonces",
    response_model=list[AnnonceResponse],
)
def list_annonces(
    syndicat_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les annonces d'un syndicat"""
    return get_annonces_by_syndicat(syndicat_id, session, skip, limit)


@router.put(
    "/annonces/{annonce_id}",
    response_model=AnnonceResponse,
)
def update_annonce_route(
    annonce_id: uuid.UUID,
    data: AnnonceUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Modifier une annonce existante"""
    return update_annonce(annonce_id, data, session)


@router.delete(
    "/annonces/{annonce_id}",
    status_code=204,
)
def delete_annonce_route(
    annonce_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Supprimer une annonce"""
    delete_annonce(annonce_id, session)
