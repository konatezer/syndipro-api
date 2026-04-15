# app/api/auth.py
from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.database import get_session
from app.models.user import User
from app.schemas.auth import (
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
    UserRegister,
    UserResponse,
)
from app.services.auth import (
    authenticate_user,
    get_current_user,
    issue_tokens,
    refresh_tokens,
    register_user,
    revoke_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", response_model=UserResponse)
def register(data: UserRegister, session: Session = Depends(get_session)):
    """Créer un nouveau compte utilisateur."""
    return register_user(data, session)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Se connecter et obtenir une paire access_token + refresh_token.

    - access_token : JWT, valide 15 minutes
    - refresh_token : opaque, valide 7 jours, rotation à chaque utilisation
    """
    user = authenticate_user(form_data.username, form_data.password, session)
    return issue_tokens(user, session)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, session: Session = Depends(get_session)):
    """Renouveler la session à partir d'un refresh token.

    - Valide et révoque l'ancien refresh token (rotation)
    - Émet une nouvelle paire access + refresh
    """
    return refresh_tokens(data.refresh_token, session)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: LogoutRequest, session: Session = Depends(get_session)):
    """Déconnecter l'utilisateur en révoquant son refresh token."""
    revoke_refresh_token(data.refresh_token, session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Obtenir le profil de l'utilisateur connecté (requiert un JWT valide)."""
    return current_user
