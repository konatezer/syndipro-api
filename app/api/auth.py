# app/api/auth.py
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.database import get_session
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import TokenResponse, UserRegister, UserResponse
from app.services.auth import authenticate_user, get_current_user, register_user

# Crée un "routeur" — un groupe de routes liées à l'auth
router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", response_model=UserResponse)
def register(data: UserRegister, session: Session = Depends(get_session)):
    """
    Créer un nouveau compte utilisateur.

    - Vérifie que l'email n'est pas déjà utilisé
    - Hache le mot de passe
    - Retourne les infos du nouvel utilisateur
    """
    user = register_user(data, session)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Se connecter et obtenir un token JWT.

    - Vérifie email + mot de passe
    - Retourne un token valide 30 minutes
    """
    user = authenticate_user(form_data.username, form_data.password, session)

    # Crée le token avec l'ID de l'utilisateur
    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Obtenir le profil de l'utilisateur connecté.

    - Requiert un token JWT valide dans le header
    - Retourne les infos de l'utilisateur
    """
    return current_user
