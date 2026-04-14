# app/services/auth.py
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.database import get_session
from app.schemas.auth import UserRegister

# Dit à FastAPI où trouver le token dans les requêtes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def register_user(data: UserRegister, session: Session) -> User:
    """Crée un nouveau compte utilisateur"""

    # 1. Vérifie si l'email existe déjà
    existing = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà"
        )

    # 2. Crée l'utilisateur avec le mot de passe haché
    user = User(
        email=data.email,
        nom=data.nom,
        prenom=data.prenom,
        hashed_password=hash_password(data.password)
    )

    # 3. Sauvegarde dans la BDD
    session.add(user)
    session.commit()
    session.refresh(user)  # Recharge pour obtenir l'ID généré

    return user


def authenticate_user(email: str, password: str, session: Session) -> User:
    """Vérifie les identifiants et retourne l'utilisateur"""

    # 1. Cherche l'utilisateur par email
    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    # 2. Vérifie que l'utilisateur existe ET que le mot de passe est bon
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """Extrait l'utilisateur du token JWT — utilisé comme dépendance"""

    # 1. Décode le token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Récupère l'ID utilisateur du token
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )

    # 3. Cherche l'utilisateur dans la BDD
    user = session.get(User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    return user