# app/models/user.py
import uuid as uuid_pkg
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class RoleEnum(str, Enum):
    admin_ca = "admin_ca"  # Membre du CA
    coproprietaire = "coproprietaire"  # Copropriétaire
    gestionnaire = "gestionnaire"  # Gestionnaire externe


class User(SQLModel, table=True):
    """Table des utilisateurs de SyndiPro"""

    __tablename__ = "users"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    nom: str = Field(min_length=2, max_length=100)
    prenom: str = Field(min_length=2, max_length=100)
    hashed_password: str
    role: RoleEnum = Field(default=RoleEnum.coproprietaire)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
