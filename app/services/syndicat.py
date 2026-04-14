import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.syndicat import Syndicat
from app.schemas.syndicat import SyndicatCreate, SyndicatUpdate


def create_syndicat(data: SyndicatCreate, session: Session) -> Syndicat:
    """Crée un nouveau syndicat de copropriété"""
    if data.numero_syndicat:
        existing = session.exec(
            select(Syndicat).where(Syndicat.numero_syndicat == data.numero_syndicat)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un syndicat avec ce numéro existe déjà",
            )

    syndicat = Syndicat(**data.model_dump())
    session.add(syndicat)
    session.commit()
    session.refresh(syndicat)
    return syndicat


def get_syndicats(session: Session, skip: int = 0, limit: int = 50) -> list[Syndicat]:
    """Retourne la liste des syndicats actifs"""
    return list(
        session.exec(
            select(Syndicat)
            .where(Syndicat.is_active == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
        ).all()
    )


def get_syndicat(syndicat_id: uuid.UUID, session: Session) -> Syndicat:
    """Retourne un syndicat par son ID"""
    syndicat = session.get(Syndicat, syndicat_id)
    if not syndicat or not syndicat.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Syndicat non trouvé",
        )
    return syndicat


def update_syndicat(syndicat_id: uuid.UUID, data: SyndicatUpdate, session: Session) -> Syndicat:
    """Met à jour un syndicat existant"""
    syndicat = get_syndicat(syndicat_id, session)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(syndicat, key, value)

    syndicat.updated_at = datetime.now(timezone.utc)
    session.add(syndicat)
    session.commit()
    session.refresh(syndicat)
    return syndicat


def delete_syndicat(syndicat_id: uuid.UUID, session: Session) -> None:
    """Désactive un syndicat (soft delete)"""
    syndicat = get_syndicat(syndicat_id, session)
    syndicat.is_active = False
    syndicat.updated_at = datetime.now(timezone.utc)
    session.add(syndicat)
    session.commit()
