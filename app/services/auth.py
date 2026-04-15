# app/services/auth.py
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS
from app.core.database import get_session
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import TokenResponse, UserRegister

# Dit à FastAPI où trouver le token dans les requêtes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def register_user(data: UserRegister, session: Session) -> User:
    """Crée un nouveau compte utilisateur"""

    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà",
        )

    user = User(
        email=data.email,
        nom=data.nom,
        prenom=data.prenom,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(email: str, password: str, session: Session) -> User:
    """Vérifie les identifiants et retourne l'utilisateur"""
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def issue_tokens(user: User, session: Session) -> TokenResponse:
    """Émet une paire access + refresh token pour un utilisateur."""
    access_token = create_access_token(data={"sub": str(user.id)})
    raw_refresh = generate_refresh_token()

    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    session.add(refresh_record)
    session.commit()

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


def refresh_tokens(raw_refresh: str, session: Session) -> TokenResponse:
    """Valide un refresh token, le révoque (rotation), et émet une nouvelle paire.

    Si le token est invalide/expiré/révoqué, lève une 401.
    """
    token_hash = hash_refresh_token(raw_refresh)
    refresh_record = session.exec(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    ).first()

    if not refresh_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide",
        )

    now = datetime.now(timezone.utc)
    # Normaliser les datetime (sqlite strip les tz)
    expires_at = refresh_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if refresh_record.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token révoqué",
        )
    if expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expiré",
        )

    user = session.get(User, refresh_record.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur invalide",
        )

    # Rotation : révoquer l'ancien refresh token
    refresh_record.revoked_at = now
    session.add(refresh_record)

    return issue_tokens(user, session)


def revoke_refresh_token(raw_refresh: str, session: Session) -> None:
    """Révoque un refresh token (utilisé lors du logout).

    Retourne silencieusement si le token n'existe pas — évite de révéler
    son existence aux attaquants.
    """
    token_hash = hash_refresh_token(raw_refresh)
    refresh_record = session.exec(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    ).first()
    if refresh_record and refresh_record.revoked_at is None:
        refresh_record.revoked_at = datetime.now(timezone.utc)
        session.add(refresh_record)
        session.commit()


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    """Extrait l'utilisateur du token JWT — utilisé comme dépendance"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")

    user = session.get(User, uuid.UUID(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")

    return user
