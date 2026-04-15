# app/core/security.py
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


def hash_password(password: str) -> str:
    """Transforme un mot de passe en texte en un hash sécurisé"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe correspond au hash stocké"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT avec une date d'expiration"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Décode et vérifie un token JWT — retourne None si invalide"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_refresh_token() -> str:
    """Génère un refresh token opaque (64 octets = 512 bits d'entropie).

    Le token brut n'est jamais stocké en BDD — seul son hash SHA-256 l'est.
    """
    return secrets.token_urlsafe(64)


def hash_refresh_token(raw_token: str) -> str:
    """Hash SHA-256 d'un refresh token pour stockage sécurisé en BDD."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
