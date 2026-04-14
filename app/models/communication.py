import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Annonce(SQLModel, table=True):
    """Table des annonces d'un syndicat"""

    __tablename__ = "annonces"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", index=True)
    auteur_id: uuid_pkg.UUID = Field(foreign_key="users.id", index=True)
    titre: str = Field(max_length=200)
    contenu: str = Field(max_length=5000)
    est_epinglee: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
