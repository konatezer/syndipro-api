import uuid

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.models.user import User
from app.schemas.syndicat import SyndicatCreate, SyndicatResponse, SyndicatUpdate
from app.services.auth import get_current_user
from app.services.syndicat import (
    create_syndicat,
    delete_syndicat,
    get_syndicat,
    get_syndicats,
    update_syndicat,
)

router = APIRouter(prefix="/syndicats", tags=["Syndicats"])


@router.post("/", response_model=SyndicatResponse, status_code=201)
def create(
    data: SyndicatCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Créer un nouveau syndicat de copropriété"""
    return create_syndicat(data, session)


@router.get("/", response_model=list[SyndicatResponse])
def list_all(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister tous les syndicats"""
    return get_syndicats(session, skip, limit)


@router.get("/{syndicat_id}", response_model=SyndicatResponse)
def get_one(
    syndicat_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Obtenir les détails d'un syndicat"""
    return get_syndicat(syndicat_id, session)


@router.put("/{syndicat_id}", response_model=SyndicatResponse)
def update(
    syndicat_id: uuid.UUID,
    data: SyndicatUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Modifier un syndicat existant"""
    return update_syndicat(syndicat_id, data, session)


@router.delete("/{syndicat_id}", status_code=204)
def delete(
    syndicat_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Supprimer un syndicat (désactivation)"""
    delete_syndicat(syndicat_id, session)
