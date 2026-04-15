import uuid

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.models.user import User
from app.schemas.membre import (
    MembreCreate,
    MembreCreateByEmail,
    MembreDetailResponse,
    MembreResponse,
    MembreUpdate,
)
from app.services.auth import get_current_user
from app.services.membre import (
    add_membre,
    add_membre_by_email,
    get_membres_syndicat,
    get_syndicats_for_user,
    remove_membre,
    update_membre,
)

router = APIRouter(tags=["Membres"])


@router.post(
    "/syndicats/{syndicat_id}/membres",
    response_model=MembreResponse,
    status_code=201,
)
def create_membre(
    syndicat_id: uuid.UUID,
    data: MembreCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Ajouter un membre à un syndicat (par user_id UUID)"""
    return add_membre(syndicat_id, data, session)


@router.post(
    "/syndicats/{syndicat_id}/membres/by-email",
    response_model=MembreResponse,
    status_code=201,
)
def create_membre_by_email(
    syndicat_id: uuid.UUID,
    data: MembreCreateByEmail,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Ajouter un membre à un syndicat en cherchant l'utilisateur par email.

    UX admin-friendly : les gestionnaires n'ont pas besoin des UUIDs.
    """
    return add_membre_by_email(syndicat_id, data, session)


@router.get(
    "/syndicats/{syndicat_id}/membres",
    response_model=list[MembreDetailResponse],
)
def list_membres(
    syndicat_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les membres d'un syndicat"""
    return get_membres_syndicat(syndicat_id, session)


@router.get(
    "/users/me/syndicats",
    response_model=list[MembreDetailResponse],
)
def my_syndicats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lister les syndicats de l'utilisateur connecté"""
    return get_syndicats_for_user(current_user.id, session)


@router.put("/membres/{membre_id}", response_model=MembreResponse)
def update(
    membre_id: uuid.UUID,
    data: MembreUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Modifier le rôle d'un membre"""
    return update_membre(membre_id, data, session)


@router.delete("/membres/{membre_id}", status_code=204)
def delete(
    membre_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Retirer un membre d'un syndicat"""
    remove_membre(membre_id, session)
