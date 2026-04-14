# app/schemas/auth.py
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.user import RoleEnum

# --- CE QUE L'UTILISATEUR ENVOIE ---

class UserRegister(BaseModel):
    """Données requises pour créer un compte"""
    email: str          # EmailStr si tu ajoutes: uv add pydantic[email]
    nom: str
    prenom: str
    password: str       # Mot de passe en clair (sera haché)


class UserLogin(BaseModel):
    """Données requises pour se connecter"""
    email: str
    password: str


# --- CE QUE L'API RETOURNE ---

class UserResponse(BaseModel):
    """Données retournées (JAMAIS le mot de passe!)"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nom: str
    prenom: str
    role: RoleEnum
    is_active: bool


class TokenResponse(BaseModel):
    """Token retourné après connexion"""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Message simple de confirmation"""
    message: str