# app/models/user.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    admin_ca = "admin_ca"          # Membre du CA
    coproprietaire = "coproprietaire"  # Copropriétaire
    gestionnaire = "gestionnaire"  # Gestionnaire externe


class User(SQLModel, table=True):
    """Table des utilisateurs de SyndiPro"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    nom: str = Field(min_length=2, max_length=100)
    prenom: str = Field(min_length=2, max_length=100)
    hashed_password: str
    role: RoleEnum = Field(default=RoleEnum.coproprietaire)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)