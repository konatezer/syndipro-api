import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.finance import CategorieDepense, StatutCotisation

# ── Cotisation ──────────────────────────────────────────────────────


class CotisationCreate(BaseModel):
    """Données pour créer une cotisation"""

    unite_id: uuid.UUID
    montant: float
    mois: int
    annee: int
    date_echeance: date


class CotisationUpdate(BaseModel):
    """Données pour modifier une cotisation (statut, paiement)"""

    statut: Optional[StatutCotisation] = None
    date_paiement: Optional[date] = None
    montant: Optional[float] = None


class CotisationResponse(BaseModel):
    """Données retournées pour une cotisation"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    syndicat_id: uuid.UUID
    unite_id: uuid.UUID
    montant: float
    mois: int
    annee: int
    statut: StatutCotisation
    date_echeance: date
    date_paiement: Optional[date]
    created_at: datetime


# ── Dépense ─────────────────────────────────────────────────────────


class DepenseCreate(BaseModel):
    """Données pour créer une dépense"""

    description: str
    montant: float
    categorie: CategorieDepense
    date_depense: date
    fournisseur: Optional[str] = None


class DepenseUpdate(BaseModel):
    """Données pour modifier une dépense"""

    description: Optional[str] = None
    montant: Optional[float] = None
    categorie: Optional[CategorieDepense] = None
    date_depense: Optional[date] = None
    fournisseur: Optional[str] = None


class DepenseResponse(BaseModel):
    """Données retournées pour une dépense"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    syndicat_id: uuid.UUID
    description: str
    montant: float
    categorie: CategorieDepense
    date_depense: date
    fournisseur: Optional[str]
    created_at: datetime


# ── Fonds de prévoyance ─────────────────────────────────────────────


class FondsPrevoyanceCreate(BaseModel):
    """Données pour créer un fonds de prévoyance"""

    solde_actuel: float = 0
    contribution_mensuelle: float = 0
    objectif_25_ans: Optional[float] = None
    derniere_etude: Optional[date] = None
    prochaine_etude: Optional[date] = None


class FondsPrevoyanceUpdate(BaseModel):
    """Données pour modifier le fonds de prévoyance"""

    solde_actuel: Optional[float] = None
    contribution_mensuelle: Optional[float] = None
    objectif_25_ans: Optional[float] = None
    derniere_etude: Optional[date] = None
    prochaine_etude: Optional[date] = None


class FondsPrevoyanceResponse(BaseModel):
    """Données retournées pour le fonds de prévoyance"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    syndicat_id: uuid.UUID
    solde_actuel: float
    contribution_mensuelle: float
    objectif_25_ans: Optional[float]
    derniere_etude: Optional[date]
    prochaine_etude: Optional[date]
    updated_at: datetime


# ── Bilan financier ─────────────────────────────────────────────────


class BilanFinancier(BaseModel):
    """Résumé financier d'un syndicat"""

    syndicat_id: uuid.UUID
    total_cotisations_attendues: float
    total_cotisations_recues: float
    total_depenses: float
    solde: float
    cotisations_en_retard: int
    cotisations_en_attente: int
    fonds_prevoyance_solde: Optional[float]
