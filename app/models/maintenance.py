import enum
import uuid as uuid_pkg
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class UrgenceMaintenance(str, enum.Enum):
    """Niveau d'urgence d'une demande de maintenance"""

    basse = "basse"
    normale = "normale"
    haute = "haute"
    urgente = "urgente"


class StatutMaintenance(str, enum.Enum):
    """Statut d'une demande de maintenance"""

    soumise = "soumise"
    en_cours = "en_cours"
    assignee = "assignee"
    completee = "completee"


class DemandeMaintenance(SQLModel, table=True):
    """Table des demandes de maintenance pour un syndicat"""

    __tablename__ = "demandes_maintenance"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", index=True)
    demandeur_id: uuid_pkg.UUID = Field(foreign_key="users.id", index=True)
    titre: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    urgence: UrgenceMaintenance = Field(default=UrgenceMaintenance.normale)
    statut: StatutMaintenance = Field(default=StatutMaintenance.soumise)
    assignee_a: Optional[str] = Field(default=None, max_length=200)
    date_soumission: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    date_completion: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Document(SQLModel, table=True):
    """Table des documents d'un syndicat"""

    __tablename__ = "documents"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", index=True)
    uploaded_by_id: uuid_pkg.UUID = Field(foreign_key="users.id", index=True)
    nom: str = Field(max_length=300)
    categorie: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    taille_octets: Optional[int] = Field(default=None)
    url_fichier: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
