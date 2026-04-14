import uuid

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.models.user import User
from app.schemas.maintenance import (
    DemandeMaintenanceCreate,
    DemandeMaintenanceResponse,
    DemandeMaintenanceUpdate,
    DocumentCreate,
    DocumentResponse,
)
from app.services.auth import get_current_user
from app.services.maintenance import (
    create_demande_maintenance,
    create_document,
    get_demandes_by_syndicat,
    get_document,
    get_documents_by_syndicat,
    update_demande_maintenance,
)

router = APIRouter(tags=["Maintenance & Documents"])


# ── Demandes de maintenance ────────────────────────────────────────


@router.post(
    "/syndicats/{syndicat_id}/maintenance",
    response_model=DemandeMaintenanceResponse,
    status_code=201,
)
def create_demande_route(
    syndicat_id: uuid.UUID,
    data: DemandeMaintenanceCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Créer une demande de maintenance pour un syndicat"""
    return create_demande_maintenance(syndicat_id, current_user.id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/maintenance",
    response_model=list[DemandeMaintenanceResponse],
)
def list_demandes(
    syndicat_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les demandes de maintenance d'un syndicat"""
    return get_demandes_by_syndicat(syndicat_id, session, skip, limit)


@router.put(
    "/maintenance/{demande_id}",
    response_model=DemandeMaintenanceResponse,
)
def update_demande_route(
    demande_id: uuid.UUID,
    data: DemandeMaintenanceUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Modifier une demande de maintenance"""
    return update_demande_maintenance(demande_id, data, session)


# ── Documents ──────────────────────────────────────────────────────


@router.post(
    "/syndicats/{syndicat_id}/documents",
    response_model=DocumentResponse,
    status_code=201,
)
def create_document_route(
    syndicat_id: uuid.UUID,
    data: DocumentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Créer un document pour un syndicat"""
    return create_document(syndicat_id, current_user.id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/documents",
    response_model=list[DocumentResponse],
)
def list_documents(
    syndicat_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les documents d'un syndicat"""
    return get_documents_by_syndicat(syndicat_id, session, skip, limit)


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
def get_document_route(
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Obtenir un document par son ID"""
    return get_document(document_id, session)
