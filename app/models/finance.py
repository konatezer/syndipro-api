import enum
import uuid as uuid_pkg
from datetime import date, datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class CategorieDepense(str, enum.Enum):
    """Catégories de dépenses pour un syndicat de copropriété"""

    administration = "administration"
    entretien = "entretien"
    assurance = "assurance"
    energie = "energie"
    professionnel = "professionnel"
    autre = "autre"


class StatutCotisation(str, enum.Enum):
    """Statut de paiement d'une cotisation"""

    en_attente = "en_attente"
    payee = "payee"
    en_retard = "en_retard"


class Cotisation(SQLModel, table=True):
    """Table des cotisations mensuelles (charges de copropriété)"""

    __tablename__ = "cotisations"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", index=True)
    unite_id: uuid_pkg.UUID = Field(foreign_key="unites.id", index=True)
    montant: float = Field(ge=0)
    mois: int = Field(ge=1, le=12)
    annee: int = Field(ge=2000)
    statut: StatutCotisation = Field(default=StatutCotisation.en_attente)
    date_echeance: date
    date_paiement: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Depense(SQLModel, table=True):
    """Table des dépenses du syndicat"""

    __tablename__ = "depenses"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", index=True)
    description: str = Field(max_length=500)
    montant: float = Field(ge=0)
    categorie: CategorieDepense
    date_depense: date
    fournisseur: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FondsPrevoyance(SQLModel, table=True):
    """Table du fonds de prévoyance (obligatoire selon la Loi 16 au Québec)"""

    __tablename__ = "fonds_prevoyance"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", unique=True, index=True)
    solde_actuel: float = Field(ge=0, default=0)
    contribution_mensuelle: float = Field(ge=0, default=0)
    objectif_25_ans: Optional[float] = Field(default=None, ge=0)
    derniere_etude: Optional[date] = Field(default=None)
    prochaine_etude: Optional[date] = Field(default=None)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
