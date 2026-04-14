import enum
import uuid as uuid_pkg
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class StatutAssemblee(str, enum.Enum):
    """Statut d'une assemblée de copropriété"""

    planifiee = "planifiee"
    en_cours = "en_cours"
    terminee = "terminee"
    annulee = "annulee"


class TypeAssemblee(str, enum.Enum):
    """Type d'assemblée générale"""

    annuelle = "annuelle"
    speciale = "speciale"
    extraordinaire = "extraordinaire"


class TypeVote(str, enum.Enum):
    """Type de vote sur une résolution"""

    pour = "pour"
    contre = "contre"
    abstention = "abstention"


class Assemblee(SQLModel, table=True):
    """Table des assemblées générales de copropriété"""

    __tablename__ = "assemblees"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", index=True)
    titre: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    type_assemblee: TypeAssemblee
    date_assemblee: datetime
    lieu: Optional[str] = Field(default=None, max_length=300)
    statut: StatutAssemblee = Field(default=StatutAssemblee.planifiee)
    quorum_requis: float = Field(default=50.0, ge=0, le=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Resolution(SQLModel, table=True):
    """Table des résolutions soumises au vote lors d'une assemblée"""

    __tablename__ = "resolutions"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    assemblee_id: uuid_pkg.UUID = Field(foreign_key="assemblees.id", index=True)
    titre: str = Field(max_length=300)
    description: Optional[str] = Field(default=None, max_length=2000)
    ordre: int = Field(ge=1)
    est_adoptee: Optional[bool] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Vote(SQLModel, table=True):
    """Table des votes individuels sur les résolutions"""

    __tablename__ = "votes"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    resolution_id: uuid_pkg.UUID = Field(foreign_key="resolutions.id", index=True)
    user_id: uuid_pkg.UUID = Field(foreign_key="users.id", index=True)
    type_vote: TypeVote
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
