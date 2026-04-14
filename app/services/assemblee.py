import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.assemblee import Assemblee, Resolution, TypeVote, Vote
from app.models.syndicat import Syndicat
from app.schemas.assemblee import (
    AssembleeCreate,
    AssembleeDetailResponse,
    AssembleeUpdate,
    ResolutionAvecResultat,
    ResolutionCreate,
    ResultatVote,
    VoteCreate,
)

# ── Helpers ─────────────────────────────────────────────────────────


def _check_syndicat(syndicat_id: uuid.UUID, session: Session) -> Syndicat:
    """Vérifie qu'un syndicat existe et est actif"""
    syndicat = session.get(Syndicat, syndicat_id)
    if not syndicat or not syndicat.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Syndicat non trouvé",
        )
    return syndicat


def _check_assemblee(assemblee_id: uuid.UUID, session: Session) -> Assemblee:
    """Vérifie qu'une assemblée existe"""
    assemblee = session.get(Assemblee, assemblee_id)
    if not assemblee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assemblée non trouvée",
        )
    return assemblee


def _check_resolution(resolution_id: uuid.UUID, session: Session) -> Resolution:
    """Vérifie qu'une résolution existe"""
    resolution = session.get(Resolution, resolution_id)
    if not resolution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Résolution non trouvée",
        )
    return resolution


# ── Assemblées ─────────────────────────────────────────────────────


def create_assemblee(syndicat_id: uuid.UUID, data: AssembleeCreate, session: Session) -> Assemblee:
    """Crée une nouvelle assemblée pour un syndicat"""
    _check_syndicat(syndicat_id, session)

    assemblee = Assemblee(syndicat_id=syndicat_id, **data.model_dump())
    session.add(assemblee)
    session.commit()
    session.refresh(assemblee)
    return assemblee


def get_assemblees_by_syndicat(
    syndicat_id: uuid.UUID,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Assemblee]:
    """Retourne les assemblées d'un syndicat"""
    return list(
        session.exec(
            select(Assemblee).where(Assemblee.syndicat_id == syndicat_id).offset(skip).limit(limit)
        ).all()
    )


def get_assemblee(assemblee_id: uuid.UUID, session: Session) -> Assemblee:
    """Retourne une assemblée par son ID"""
    return _check_assemblee(assemblee_id, session)


def update_assemblee(assemblee_id: uuid.UUID, data: AssembleeUpdate, session: Session) -> Assemblee:
    """Met à jour une assemblée existante"""
    assemblee = _check_assemblee(assemblee_id, session)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assemblee, key, value)

    session.add(assemblee)
    session.commit()
    session.refresh(assemblee)
    return assemblee


# ── Résolutions ────────────────────────────────────────────────────


def add_resolution(assemblee_id: uuid.UUID, data: ResolutionCreate, session: Session) -> Resolution:
    """Ajoute une résolution à une assemblée"""
    _check_assemblee(assemblee_id, session)

    resolution = Resolution(assemblee_id=assemblee_id, **data.model_dump())
    session.add(resolution)
    session.commit()
    session.refresh(resolution)
    return resolution


def get_resolutions(assemblee_id: uuid.UUID, session: Session) -> list[Resolution]:
    """Retourne les résolutions d'une assemblée, triées par ordre"""
    return list(
        session.exec(
            select(Resolution)
            .where(Resolution.assemblee_id == assemblee_id)
            .order_by(Resolution.ordre)
        ).all()
    )


# ── Votes ──────────────────────────────────────────────────────────


def submit_vote(
    resolution_id: uuid.UUID,
    user_id: uuid.UUID,
    data: VoteCreate,
    session: Session,
) -> Vote:
    """Soumet un vote sur une résolution (un seul vote par utilisateur)"""
    _check_resolution(resolution_id, session)

    # Vérifie qu'il n'y a pas déjà un vote de cet utilisateur
    existing = session.exec(
        select(Vote).where(
            Vote.resolution_id == resolution_id,
            Vote.user_id == user_id,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà voté sur cette résolution",
        )

    vote = Vote(
        resolution_id=resolution_id,
        user_id=user_id,
        type_vote=data.type_vote,
    )
    session.add(vote)
    session.commit()
    session.refresh(vote)
    return vote


def get_resultat_vote(resolution_id: uuid.UUID, session: Session) -> ResultatVote:
    """Compte les votes et détermine si la résolution est adoptée"""
    _check_resolution(resolution_id, session)

    votes = list(session.exec(select(Vote).where(Vote.resolution_id == resolution_id)).all())

    pour = sum(1 for v in votes if v.type_vote == TypeVote.pour)
    contre = sum(1 for v in votes if v.type_vote == TypeVote.contre)
    abstention = sum(1 for v in votes if v.type_vote == TypeVote.abstention)

    # Majorité simple : plus de pour que de contre (abstentions non comptées)
    est_adoptee = pour > contre

    return ResultatVote(
        resolution_id=resolution_id,
        pour=pour,
        contre=contre,
        abstention=abstention,
        est_adoptee=est_adoptee,
    )


# ── Détail assemblée ──────────────────────────────────────────────


def get_assemblee_detail(assemblee_id: uuid.UUID, session: Session) -> AssembleeDetailResponse:
    """Retourne une assemblée avec toutes ses résolutions et résultats"""
    assemblee = _check_assemblee(assemblee_id, session)
    resolutions = get_resolutions(assemblee_id, session)

    resolutions_avec_resultats = []
    for resolution in resolutions:
        # Calcule le résultat de vote pour chaque résolution
        votes = list(session.exec(select(Vote).where(Vote.resolution_id == resolution.id)).all())

        resultat = None
        if votes:
            pour = sum(1 for v in votes if v.type_vote == TypeVote.pour)
            contre = sum(1 for v in votes if v.type_vote == TypeVote.contre)
            abstention_count = sum(1 for v in votes if v.type_vote == TypeVote.abstention)
            resultat = ResultatVote(
                resolution_id=resolution.id,
                pour=pour,
                contre=contre,
                abstention=abstention_count,
                est_adoptee=pour > contre,
            )

        resolutions_avec_resultats.append(
            ResolutionAvecResultat(
                id=resolution.id,
                assemblee_id=resolution.assemblee_id,
                titre=resolution.titre,
                description=resolution.description,
                ordre=resolution.ordre,
                est_adoptee=resolution.est_adoptee,
                created_at=resolution.created_at,
                resultat=resultat,
            )
        )

    return AssembleeDetailResponse(
        id=assemblee.id,
        syndicat_id=assemblee.syndicat_id,
        titre=assemblee.titre,
        description=assemblee.description,
        type_assemblee=assemblee.type_assemblee,
        date_assemblee=assemblee.date_assemblee,
        lieu=assemblee.lieu,
        statut=assemblee.statut,
        quorum_requis=assemblee.quorum_requis,
        created_at=assemblee.created_at,
        resolutions=resolutions_avec_resultats,
    )
