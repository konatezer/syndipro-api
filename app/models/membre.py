import uuid as uuid_pkg
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.syndicat import Syndicat
    from app.models.user import User


class RoleSyndicat(str, Enum):
    president = "president"
    tresorier = "tresorier"
    secretaire = "secretaire"
    administrateur = "administrateur"
    coproprietaire = "coproprietaire"


class MembreSyndicat(SQLModel, table=True):
    """Table de liaison entre utilisateurs et syndicats (many-to-many)"""

    __tablename__ = "membres_syndicat"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    user_id: uuid_pkg.UUID = Field(foreign_key="users.id", index=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", index=True)
    role_syndicat: RoleSyndicat = Field(default=RoleSyndicat.coproprietaire)
    is_active: bool = Field(default=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional["User"] = Relationship()
    syndicat: Optional["Syndicat"] = Relationship()
