import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.membre import RoleSyndicat


class MembreCreate(BaseModel):
    """Ajouter un utilisateur à un syndicat"""

    user_id: uuid.UUID
    role_syndicat: RoleSyndicat = RoleSyndicat.coproprietaire


class MembreUpdate(BaseModel):
    """Modifier le rôle d'un membre"""

    role_syndicat: Optional[RoleSyndicat] = None


class MembreResponse(BaseModel):
    """Données retournées pour un membre"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    syndicat_id: uuid.UUID
    role_syndicat: RoleSyndicat
    is_active: bool
    joined_at: datetime


class MembreDetailResponse(BaseModel):
    """Membre avec infos utilisateur et syndicat"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    syndicat_id: uuid.UUID
    role_syndicat: RoleSyndicat
    is_active: bool
    joined_at: datetime
    user_nom: str
    user_prenom: str
    user_email: str
    syndicat_nom: str
