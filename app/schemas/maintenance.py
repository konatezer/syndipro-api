import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.maintenance import StatutMaintenance, UrgenceMaintenance

# ── Demande de maintenance ─────────────────────────────────────────


class DemandeMaintenanceCreate(BaseModel):
    """Données pour créer une demande de maintenance"""

    titre: str
    description: str
    urgence: UrgenceMaintenance = UrgenceMaintenance.normale


class DemandeMaintenanceUpdate(BaseModel):
    """Données pour modifier une demande de maintenance"""

    titre: Optional[str] = None
    description: Optional[str] = None
    urgence: Optional[UrgenceMaintenance] = None
    statut: Optional[StatutMaintenance] = None
    assignee_a: Optional[str] = None
    date_completion: Optional[datetime] = None


class DemandeMaintenanceResponse(BaseModel):
    """Données retournées pour une demande de maintenance"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    syndicat_id: uuid.UUID
    demandeur_id: uuid.UUID
    titre: str
    description: str
    urgence: UrgenceMaintenance
    statut: StatutMaintenance
    assignee_a: Optional[str]
    date_soumission: datetime
    date_completion: Optional[datetime]
    created_at: datetime


# ── Document ───────────────────────────────────────────────────────


class DocumentCreate(BaseModel):
    """Données pour créer un document"""

    nom: str
    categorie: str
    description: Optional[str] = None
    taille_octets: Optional[int] = None
    url_fichier: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Données pour modifier un document"""

    nom: Optional[str] = None
    categorie: Optional[str] = None
    description: Optional[str] = None
    url_fichier: Optional[str] = None


class DocumentResponse(BaseModel):
    """Données retournées pour un document"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    syndicat_id: uuid.UUID
    uploaded_by_id: uuid.UUID
    nom: str
    categorie: str
    description: Optional[str]
    taille_octets: Optional[int]
    url_fichier: Optional[str]
    created_at: datetime
