import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.syndicat import Syndicat
from app.models.unite import Unite
from app.schemas.unite import UniteCreate, UniteUpdate


def create_unite(syndicat_id: uuid.UUID, data: UniteCreate, session: Session) -> Unite:
    """Crée une nouvelle unité dans un syndicat"""
    syndicat = session.get(Syndicat, syndicat_id)
    if not syndicat or not syndicat.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Syndicat non trouvé",
        )

    existing = session.exec(
        select(Unite).where(
            Unite.syndicat_id == syndicat_id,
            Unite.numero == data.numero,
            Unite.is_active == True,  # noqa: E712
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"L'unité {data.numero} existe déjà dans ce syndicat",
        )

    unite = Unite(syndicat_id=syndicat_id, **data.model_dump())
    session.add(unite)
    session.commit()
    session.refresh(unite)
    return unite


def get_unites_by_syndicat(
    syndicat_id: uuid.UUID, session: Session, skip: int = 0, limit: int = 100
) -> list[Unite]:
    """Retourne les unités d'un syndicat"""
    return list(
        session.exec(
            select(Unite)
            .where(Unite.syndicat_id == syndicat_id, Unite.is_active == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
        ).all()
    )


def get_unite(unite_id: uuid.UUID, session: Session) -> Unite:
    """Retourne une unité par son ID"""
    unite = session.get(Unite, unite_id)
    if not unite or not unite.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unité non trouvée",
        )
    return unite


def update_unite(unite_id: uuid.UUID, data: UniteUpdate, session: Session) -> Unite:
    """Met à jour une unité existante"""
    unite = get_unite(unite_id, session)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(unite, key, value)

    session.add(unite)
    session.commit()
    session.refresh(unite)
    return unite
