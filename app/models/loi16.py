import enum
import uuid as uuid_pkg
from datetime import date, datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class CategorieComposante(str, enum.Enum):
    """Catégories de composantes d'immeuble selon la Loi 16"""

    structure = "structure"
    enveloppe = "enveloppe"
    mecanique = "mecanique"
    electrique = "electrique"
    plomberie = "plomberie"
    toiture = "toiture"
    stationnement = "stationnement"
    amenagement = "amenagement"
    ascenseur = "ascenseur"
    autre = "autre"


class EtatComposante(str, enum.Enum):
    """État d'une composante d'immeuble"""

    bon = "bon"
    acceptable = "acceptable"
    a_surveiller = "a_surveiller"
    a_remplacer = "a_remplacer"
    critique = "critique"


class ComposanteImmeuble(SQLModel, table=True):
    """Table des composantes d'immeuble pour le carnet d'entretien (Loi 16)"""

    __tablename__ = "composantes_immeuble"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", index=True)
    nom: str = Field(max_length=200)
    categorie: CategorieComposante
    description: Optional[str] = Field(default=None, max_length=1000)
    annee_installation: Optional[int] = Field(default=None)
    duree_vie_estimee: Optional[int] = Field(default=None)
    etat: EtatComposante = Field(default=EtatComposante.bon)
    cout_remplacement_estime: Optional[float] = Field(default=None)
    derniere_inspection: Optional[date] = Field(default=None)
    prochaine_inspection: Optional[date] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EntreeCarnet(SQLModel, table=True):
    """Table des entrées du carnet d'entretien (Loi 16)"""

    __tablename__ = "entrees_carnet"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    composante_id: uuid_pkg.UUID = Field(foreign_key="composantes_immeuble.id", index=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", index=True)
    type_intervention: str = Field(max_length=100)
    description: str = Field(max_length=2000)
    date_intervention: date
    cout: Optional[float] = Field(default=None)
    effectue_par: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScoreConformite(SQLModel, table=True):
    """Table du score de conformité Loi 16 pour un syndicat"""

    __tablename__ = "scores_conformite"

    id: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    syndicat_id: uuid_pkg.UUID = Field(foreign_key="syndicats.id", unique=True, index=True)
    score_global: float = Field(ge=0, le=100, default=0)
    carnet_entretien_ok: bool = Field(default=False)
    fonds_prevoyance_ok: bool = Field(default=False)
    etude_fonds_a_jour: bool = Field(default=False)
    attestation_disponible: bool = Field(default=False)
    derniere_evaluation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recommandations: Optional[str] = Field(default=None, max_length=5000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
