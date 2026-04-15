import uuid as uuid_pkg
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class RefreshToken(SQLModel, table=True):
    """Refresh tokens pour la rotation des sessions utilisateur.

    On stocke uniquement le hash SHA-256 du token, jamais le raw.
    Chaque refresh token a une durée de vie limitée (7 jours par défaut).
    """

    __tablename__ = "refresh_tokens"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    user_id: uuid_pkg.UUID = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(unique=True, index=True, max_length=128)
    expires_at: datetime
    revoked_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
