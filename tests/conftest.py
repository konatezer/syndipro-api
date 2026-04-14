import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.database import get_session
from app.models import (  # noqa: F401
    Annonce,
    Assemblee,
    ComposanteImmeuble,
    Cotisation,
    DemandeMaintenance,
    Depense,
    Document,
    EntreeCarnet,
    FondsPrevoyance,
    MembreSyndicat,
    Resolution,
    ScoreConformite,
    Syndicat,
    Unite,
    User,
    Vote,
)
from main import app


@pytest.fixture(name="session")
def session_fixture():
    """Crée une base de données SQLite en mémoire pour chaque test"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Crée un client de test avec la session de test injectée"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient):
    """Crée un utilisateur et retourne les headers d'authentification"""
    client.post(
        "/auth/register",
        json={
            "email": "test@syndipro.qc",
            "nom": "Tremblay",
            "prenom": "Jean",
            "password": "TestPass123!",
        },
    )
    response = client.post(
        "/auth/login",
        data={"username": "test@syndipro.qc", "password": "TestPass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
