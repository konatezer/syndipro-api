import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.assemblee import StatutAssemblee, TypeAssemblee, TypeVote

# ── Assemblée ──────────────────────────────────────────────────────


class AssembleeCreate(BaseModel):
    """Données pour créer une assemblée"""

    titre: str
    description: Optional[str] = None
    type_assemblee: TypeAssemblee
    date_assemblee: datetime
    lieu: Optional[str] = None
    quorum_requis: float = 50.0


class AssembleeUpdate(BaseModel):
    """Données pour modifier une assemblée"""

    titre: Optional[str] = None
    description: Optional[str] = None
    type_assemblee: Optional[TypeAssemblee] = None
    date_assemblee: Optional[datetime] = None
    lieu: Optional[str] = None
    statut: Optional[StatutAssemblee] = None
    quorum_requis: Optional[float] = None


class AssembleeResponse(BaseModel):
    """Données retournées pour une assemblée"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    syndicat_id: uuid.UUID
    titre: str
    description: Optional[str]
    type_assemblee: TypeAssemblee
    date_assemblee: datetime
    lieu: Optional[str]
    statut: StatutAssemblee
    quorum_requis: float
    created_at: datetime


# ── Résolution ─────────────────────────────────────────────────────


class ResolutionCreate(BaseModel):
    """Données pour créer une résolution"""

    titre: str
    description: Optional[str] = None
    ordre: int


class ResolutionResponse(BaseModel):
    """Données retournées pour une résolution"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assemblee_id: uuid.UUID
    titre: str
    description: Optional[str]
    ordre: int
    est_adoptee: Optional[bool]
    created_at: datetime


# ── Vote ───────────────────────────────────────────────────────────


class VoteCreate(BaseModel):
    """Données pour soumettre un vote"""

    type_vote: TypeVote


class VoteResponse(BaseModel):
    """Données retournées pour un vote"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resolution_id: uuid.UUID
    user_id: uuid.UUID
    type_vote: TypeVote
    created_at: datetime


# ── Résultat de vote ───────────────────────────────────────────────


class ResultatVote(BaseModel):
    """Résultat du dépouillement d'une résolution"""

    resolution_id: uuid.UUID
    pour: int
    contre: int
    abstention: int
    est_adoptee: bool


# ── Détail assemblée ──────────────────────────────────────────────


class ResolutionAvecResultat(BaseModel):
    """Résolution avec son résultat de vote"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assemblee_id: uuid.UUID
    titre: str
    description: Optional[str]
    ordre: int
    est_adoptee: Optional[bool]
    created_at: datetime
    resultat: Optional[ResultatVote] = None


class AssembleeDetailResponse(BaseModel):
    """Assemblée complète avec résolutions et résultats de votes"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    syndicat_id: uuid.UUID
    titre: str
    description: Optional[str]
    type_assemblee: TypeAssemblee
    date_assemblee: datetime
    lieu: Optional[str]
    statut: StatutAssemblee
    quorum_requis: float
    created_at: datetime
    resolutions: list[ResolutionAvecResultat]
