import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SyndicatCreate(BaseModel):
    """Données pour créer un syndicat"""

    nom: str
    adresse: str
    ville: str = "Montréal"
    province: str = "Québec"
    code_postal: str
    nombre_unites: int
    numero_syndicat: Optional[str] = None


class SyndicatUpdate(BaseModel):
    """Données pour modifier un syndicat (tous les champs optionnels)"""

    nom: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    province: Optional[str] = None
    code_postal: Optional[str] = None
    nombre_unites: Optional[int] = None
    numero_syndicat: Optional[str] = None


class SyndicatResponse(BaseModel):
    """Données retournées pour un syndicat"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nom: str
    adresse: str
    ville: str
    province: str
    code_postal: str
    nombre_unites: int
    numero_syndicat: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
