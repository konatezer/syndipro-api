# app/schemas/auth.py
import uuid

from pydantic import BaseModel, ConfigDict

from app.models.user import RoleEnum

# --- CE QUE L'UTILISATEUR ENVOIE ---


class UserRegister(BaseModel):
    """Données requises pour créer un compte"""

    email: str  # EmailStr si tu ajoutes: uv add pydantic[email]
    nom: str
    prenom: str
    password: str  # Mot de passe en clair (sera haché)


class UserLogin(BaseModel):
    """Données requises pour se connecter"""

    email: str
    password: str


# --- CE QUE L'API RETOURNE ---


class UserResponse(BaseModel):
    """Données retournées (JAMAIS le mot de passe!)"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    nom: str
    prenom: str
    role: RoleEnum
    is_active: bool


class TokenResponse(BaseModel):
    """Token retourné après connexion ou refresh.

    Contient l'access_token (JWT 15 min) et le refresh_token (opaque 7 jours).
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Payload pour POST /auth/refresh"""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Payload pour POST /auth/logout — révoque le refresh token"""

    refresh_token: str


class MessageResponse(BaseModel):
    """Message simple de confirmation"""

    message: str
