import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.membre import MembreSyndicat
from app.models.syndicat import Syndicat
from app.models.user import User
from app.schemas.membre import (
    MembreCreate,
    MembreCreateByEmail,
    MembreDetailResponse,
    MembreUpdate,
)


def add_membre(syndicat_id: uuid.UUID, data: MembreCreate, session: Session) -> MembreSyndicat:
    """Ajoute un utilisateur comme membre d'un syndicat"""
    syndicat = session.get(Syndicat, syndicat_id)
    if not syndicat or not syndicat.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Syndicat non trouvé",
        )

    user = session.get(User, data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )

    existing = session.exec(
        select(MembreSyndicat).where(
            MembreSyndicat.user_id == data.user_id,
            MembreSyndicat.syndicat_id == syndicat_id,
            MembreSyndicat.is_active == True,  # noqa: E712
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet utilisateur est déjà membre de ce syndicat",
        )

    membre = MembreSyndicat(
        user_id=data.user_id,
        syndicat_id=syndicat_id,
        role_syndicat=data.role_syndicat,
    )
    session.add(membre)
    session.commit()
    session.refresh(membre)
    return membre


def add_membre_by_email(
    syndicat_id: uuid.UUID, data: MembreCreateByEmail, session: Session
) -> MembreSyndicat:
    """Ajoute un membre à un syndicat en cherchant l'utilisateur par email."""
    user = session.exec(select(User).where(User.email == data.user_email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucun utilisateur trouvé avec l'email {data.user_email}",
        )
    return add_membre(
        syndicat_id,
        MembreCreate(user_id=user.id, role_syndicat=data.role_syndicat),
        session,
    )


def get_membres_syndicat(syndicat_id: uuid.UUID, session: Session) -> list[MembreDetailResponse]:
    """Retourne les membres d'un syndicat avec détails"""
    membres = session.exec(
        select(MembreSyndicat).where(
            MembreSyndicat.syndicat_id == syndicat_id,
            MembreSyndicat.is_active == True,  # noqa: E712
        )
    ).all()

    result = []
    for m in membres:
        user = session.get(User, m.user_id)
        syndicat = session.get(Syndicat, m.syndicat_id)
        result.append(
            MembreDetailResponse(
                id=m.id,
                user_id=m.user_id,
                syndicat_id=m.syndicat_id,
                role_syndicat=m.role_syndicat,
                is_active=m.is_active,
                joined_at=m.joined_at,
                user_nom=user.nom if user else "",
                user_prenom=user.prenom if user else "",
                user_email=user.email if user else "",
                syndicat_nom=syndicat.nom if syndicat else "",
            )
        )
    return result


def get_syndicats_for_user(user_id: uuid.UUID, session: Session) -> list[MembreDetailResponse]:
    """Retourne les syndicats auxquels un utilisateur appartient"""
    membres = session.exec(
        select(MembreSyndicat).where(
            MembreSyndicat.user_id == user_id,
            MembreSyndicat.is_active == True,  # noqa: E712
        )
    ).all()

    result = []
    for m in membres:
        user = session.get(User, m.user_id)
        syndicat = session.get(Syndicat, m.syndicat_id)
        if syndicat and syndicat.is_active:
            result.append(
                MembreDetailResponse(
                    id=m.id,
                    user_id=m.user_id,
                    syndicat_id=m.syndicat_id,
                    role_syndicat=m.role_syndicat,
                    is_active=m.is_active,
                    joined_at=m.joined_at,
                    user_nom=user.nom if user else "",
                    user_prenom=user.prenom if user else "",
                    user_email=user.email if user else "",
                    syndicat_nom=syndicat.nom if syndicat else "",
                )
            )
    return result


def update_membre(membre_id: uuid.UUID, data: MembreUpdate, session: Session) -> MembreSyndicat:
    """Met à jour le rôle d'un membre"""
    membre = session.get(MembreSyndicat, membre_id)
    if not membre or not membre.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membre non trouvé",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(membre, key, value)

    session.add(membre)
    session.commit()
    session.refresh(membre)
    return membre


def remove_membre(membre_id: uuid.UUID, session: Session) -> None:
    """Retire un membre d'un syndicat (soft delete)"""
    membre = session.get(MembreSyndicat, membre_id)
    if not membre or not membre.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membre non trouvé",
        )
    membre.is_active = False
    session.add(membre)
    session.commit()
