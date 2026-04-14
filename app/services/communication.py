import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.communication import Annonce
from app.models.syndicat import Syndicat
from app.schemas.communication import AnnonceCreate, AnnonceUpdate

# ── Helpers ─────────────────────────────────────────────────────────


def _check_syndicat(syndicat_id: uuid.UUID, session: Session) -> Syndicat:
    """Vérifie qu'un syndicat existe et est actif"""
    syndicat = session.get(Syndicat, syndicat_id)
    if not syndicat or not syndicat.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Syndicat non trouvé",
        )
    return syndicat


# ── Annonces ───────────────────────────────────────────────────────


def create_annonce(
    syndicat_id: uuid.UUID,
    auteur_id: uuid.UUID,
    data: AnnonceCreate,
    session: Session,
) -> Annonce:
    """Crée une nouvelle annonce pour un syndicat"""
    _check_syndicat(syndicat_id, session)

    annonce = Annonce(
        syndicat_id=syndicat_id,
        auteur_id=auteur_id,
        **data.model_dump(),
    )
    session.add(annonce)
    session.commit()
    session.refresh(annonce)
    return annonce


def get_annonces_by_syndicat(
    syndicat_id: uuid.UUID,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Annonce]:
    """Retourne les annonces d'un syndicat"""
    return list(
        session.exec(
            select(Annonce).where(Annonce.syndicat_id == syndicat_id).offset(skip).limit(limit)
        ).all()
    )


def get_annonce(annonce_id: uuid.UUID, session: Session) -> Annonce:
    """Retourne une annonce par son ID"""
    annonce = session.get(Annonce, annonce_id)
    if not annonce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annonce non trouvée",
        )
    return annonce


def update_annonce(
    annonce_id: uuid.UUID,
    data: AnnonceUpdate,
    session: Session,
) -> Annonce:
    """Met à jour une annonce existante"""
    annonce = session.get(Annonce, annonce_id)
    if not annonce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annonce non trouvée",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(annonce, key, value)

    session.add(annonce)
    session.commit()
    session.refresh(annonce)
    return annonce


def delete_annonce(annonce_id: uuid.UUID, session: Session) -> None:
    """Supprime une annonce"""
    annonce = session.get(Annonce, annonce_id)
    if not annonce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annonce non trouvée",
        )

    session.delete(annonce)
    session.commit()
