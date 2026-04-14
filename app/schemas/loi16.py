import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.loi16 import CategorieComposante, EtatComposante

# ── Composante d'immeuble ─────────────────────────────────────────


class ComposanteImmeubleCreate(BaseModel):
    """Données pour créer une composante d'immeuble"""

    nom: str
    categorie: CategorieComposante
    description: Optional[str] = None
    annee_installation: Optional[int] = None
    duree_vie_estimee: Optional[int] = None
    etat: EtatComposante = EtatComposante.bon
    cout_remplacement_estime: Optional[float] = None
    derniere_inspection: Optional[date] = None
    prochaine_inspection: Optional[date] = None
    notes: Optional[str] = None


class ComposanteImmeubleUpdate(BaseModel):
    """Données pour modifier une composante d'immeuble"""

    nom: Optional[str] = None
    categorie: Optional[CategorieComposante] = None
    description: Optional[str] = None
    annee_installation: Optional[int] = None
    duree_vie_estimee: Optional[int] = None
    etat: Optional[EtatComposante] = None
    cout_remplacement_estime: Optional[float] = None
    derniere_inspection: Optional[date] = None
    prochaine_inspection: Optional[date] = None
    notes: Optional[str] = None


class ComposanteImmeubleResponse(BaseModel):
    """Données retournées pour une composante d'immeuble"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    syndicat_id: uuid.UUID
    nom: str
    categorie: CategorieComposante
    description: Optional[str]
    annee_installation: Optional[int]
    duree_vie_estimee: Optional[int]
    etat: EtatComposante
    cout_remplacement_estime: Optional[float]
    derniere_inspection: Optional[date]
    prochaine_inspection: Optional[date]
    notes: Optional[str]
    created_at: datetime


# ── Entrée du carnet d'entretien ──────────────────────────────────


class EntreeCarnetCreate(BaseModel):
    """Données pour créer une entrée dans le carnet d'entretien"""

    composante_id: uuid.UUID
    type_intervention: str
    description: str
    date_intervention: date
    cout: Optional[float] = None
    effectue_par: Optional[str] = None


class EntreeCarnetUpdate(BaseModel):
    """Données pour modifier une entrée du carnet"""

    type_intervention: Optional[str] = None
    description: Optional[str] = None
    date_intervention: Optional[date] = None
    cout: Optional[float] = None
    effectue_par: Optional[str] = None


class EntreeCarnetResponse(BaseModel):
    """Données retournées pour une entrée du carnet"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    composante_id: uuid.UUID
    syndicat_id: uuid.UUID
    type_intervention: str
    description: str
    date_intervention: date
    cout: Optional[float]
    effectue_par: Optional[str]
    created_at: datetime


# ── Score de conformité ───────────────────────────────────────────


class ScoreConformiteResponse(BaseModel):
    """Données retournées pour le score de conformité"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    syndicat_id: uuid.UUID
    score_global: float
    carnet_entretien_ok: bool
    fonds_prevoyance_ok: bool
    etude_fonds_a_jour: bool
    attestation_disponible: bool
    derniere_evaluation: datetime
    recommandations: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class ScoreConformiteDetail(BaseModel):
    """Score de conformité avec détails de calcul"""

    model_config = ConfigDict(from_attributes=True)

    score: ScoreConformiteResponse
    nombre_composantes: int
    nombre_entrees_carnet: int
    composantes_critiques: int
