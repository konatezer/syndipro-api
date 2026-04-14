import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.maintenance import (
    DemandeMaintenance,
    Document,
    StatutMaintenance,
)
from app.models.syndicat import Syndicat
from app.schemas.maintenance import (
    DemandeMaintenanceCreate,
    DemandeMaintenanceUpdate,
    DocumentCreate,
    DocumentUpdate,
)

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


# ── Demandes de maintenance ────────────────────────────────────────


def create_demande_maintenance(
    syndicat_id: uuid.UUID,
    demandeur_id: uuid.UUID,
    data: DemandeMaintenanceCreate,
    session: Session,
) -> DemandeMaintenance:
    """Crée une nouvelle demande de maintenance"""
    _check_syndicat(syndicat_id, session)

    demande = DemandeMaintenance(
        syndicat_id=syndicat_id,
        demandeur_id=demandeur_id,
        **data.model_dump(),
    )
    session.add(demande)
    session.commit()
    session.refresh(demande)
    return demande


def get_demandes_by_syndicat(
    syndicat_id: uuid.UUID,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[DemandeMaintenance]:
    """Retourne les demandes de maintenance d'un syndicat"""
    return list(
        session.exec(
            select(DemandeMaintenance)
            .where(DemandeMaintenance.syndicat_id == syndicat_id)
            .offset(skip)
            .limit(limit)
        ).all()
    )


def update_demande_maintenance(
    demande_id: uuid.UUID,
    data: DemandeMaintenanceUpdate,
    session: Session,
) -> DemandeMaintenance:
    """Met à jour une demande de maintenance avec gestion des transitions de statut"""
    demande = session.get(DemandeMaintenance, demande_id)
    if not demande:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande de maintenance non trouvée",
        )

    update_data = data.model_dump(exclude_unset=True)

    # Si le statut passe à completee, on enregistre la date de complétion
    if (
        "statut" in update_data
        and update_data["statut"] == StatutMaintenance.completee
        and demande.statut != StatutMaintenance.completee
    ):
        update_data.setdefault("date_completion", datetime.now(timezone.utc))

    for key, value in update_data.items():
        setattr(demande, key, value)

    session.add(demande)
    session.commit()
    session.refresh(demande)
    return demande


# ── Documents ──────────────────────────────────────────────────────


def create_document(
    syndicat_id: uuid.UUID,
    uploaded_by_id: uuid.UUID,
    data: DocumentCreate,
    session: Session,
) -> Document:
    """Crée un nouveau document pour un syndicat"""
    _check_syndicat(syndicat_id, session)

    document = Document(
        syndicat_id=syndicat_id,
        uploaded_by_id=uploaded_by_id,
        **data.model_dump(),
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def get_documents_by_syndicat(
    syndicat_id: uuid.UUID,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Document]:
    """Retourne les documents d'un syndicat"""
    return list(
        session.exec(
            select(Document).where(Document.syndicat_id == syndicat_id).offset(skip).limit(limit)
        ).all()
    )


def get_document(document_id: uuid.UUID, session: Session) -> Document:
    """Retourne un document par son ID"""
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document non trouvé",
        )
    return document


def update_document(
    document_id: uuid.UUID,
    data: DocumentUpdate,
    session: Session,
) -> Document:
    """Met à jour un document existant"""
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document non trouvé",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(document, key, value)

    session.add(document)
    session.commit()
    session.refresh(document)
    return document
