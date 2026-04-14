import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UniteCreate(BaseModel):
    """Données pour créer une unité"""

    numero: str
    etage: Optional[int] = None
    superficie_m2: Optional[float] = None
    quote_part: float
    description: Optional[str] = None
    proprietaire_id: Optional[uuid.UUID] = None


class UniteUpdate(BaseModel):
    """Données pour modifier une unité"""

    numero: Optional[str] = None
    etage: Optional[int] = None
    superficie_m2: Optional[float] = None
    quote_part: Optional[float] = None
    description: Optional[str] = None
    proprietaire_id: Optional[uuid.UUID] = None


class UniteResponse(BaseModel):
    """Données retournées pour une unité"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    numero: str
    etage: Optional[int]
    superficie_m2: Optional[float]
    quote_part: float
    description: Optional[str]
    is_active: bool
    created_at: datetime
    syndicat_id: uuid.UUID
    proprietaire_id: Optional[uuid.UUID]
