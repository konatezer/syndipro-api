import uuid

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.models.user import User
from app.schemas.unite import UniteCreate, UniteResponse, UniteUpdate
from app.services.auth import get_current_user
from app.services.unite import (
    create_unite,
    get_unite,
    get_unites_by_syndicat,
    update_unite,
)

router = APIRouter(tags=["Unités"])


@router.post("/syndicats/{syndicat_id}/unites", response_model=UniteResponse, status_code=201)
def create(
    syndicat_id: uuid.UUID,
    data: UniteCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Ajouter une unité à un syndicat"""
    return create_unite(syndicat_id, data, session)


@router.get("/syndicats/{syndicat_id}/unites", response_model=list[UniteResponse])
def list_by_syndicat(
    syndicat_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les unités d'un syndicat"""
    return get_unites_by_syndicat(syndicat_id, session, skip, limit)


@router.get("/unites/{unite_id}", response_model=UniteResponse)
def get_one(
    unite_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Obtenir les détails d'une unité"""
    return get_unite(unite_id, session)


@router.put("/unites/{unite_id}", response_model=UniteResponse)
def update(
    unite_id: uuid.UUID,
    data: UniteUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Modifier une unité existante"""
    return update_unite(unite_id, data, session)
