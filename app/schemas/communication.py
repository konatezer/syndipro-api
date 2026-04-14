import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

# ── Annonce ────────────────────────────────────────────────────────


class AnnonceCreate(BaseModel):
    """Données pour créer une annonce"""

    titre: str
    contenu: str
    est_epinglee: bool = False


class AnnonceUpdate(BaseModel):
    """Données pour modifier une annonce"""

    titre: Optional[str] = None
    contenu: Optional[str] = None
    est_epinglee: Optional[bool] = None


class AnnonceResponse(BaseModel):
    """Données retournées pour une annonce"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    syndicat_id: uuid.UUID
    auteur_id: uuid.UUID
    titre: str
    contenu: str
    est_epinglee: bool
    created_at: datetime
