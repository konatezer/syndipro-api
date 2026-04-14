import uuid as uuid_pkg
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.unite import Unite  # noqa: F401


class Syndicat(SQLModel, table=True):
    """Table des syndicats de copropriété"""

    __tablename__ = "syndicats"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    nom: str = Field(min_length=2, max_length=200, index=True)
    adresse: str = Field(max_length=300)
    ville: str = Field(max_length=100, default="Montréal")
    province: str = Field(max_length=50, default="Québec")
    code_postal: str = Field(max_length=10)
    nombre_unites: int = Field(ge=1)
    numero_syndicat: Optional[str] = Field(default=None, unique=True, max_length=50)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    unites: list["Unite"] = Relationship(back_populates="syndicat")
