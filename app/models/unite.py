import uuid as uuid_pkg
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.syndicat import Syndicat
    from app.models.user import User


class Unite(SQLModel, table=True):
    """Table des unités de copropriété (appartements/condos)"""

    __tablename__ = "unites"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    numero: str = Field(max_length=20)
    etage: Optional[int] = Field(default=None)
    superficie_m2: Optional[float] = Field(default=None, ge=0)
    quote_part: float = Field(ge=0, le=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", index=True)
    proprietaire_id: Optional[uuid_pkg.UUID] = Field(
        default=None, foreign_key="users.id", index=True
    )

    syndicat: Optional["Syndicat"] = Relationship(back_populates="unites")
    proprietaire: Optional["User"] = Relationship()
