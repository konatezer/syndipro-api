"""Tests pour le flux refresh token (rotation + révocation)."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken


def _register_and_login(client: TestClient) -> dict:
    """Inscrit un utilisateur et retourne le payload de login complet."""
    client.post(
        "/auth/register",
        json={
            "email": "refresh@syndipro.qc",
            "nom": "Durand",
            "prenom": "Léa",
            "password": "MotDePasse123!",
        },
    )
    resp = client.post(
        "/auth/login",
        data={"username": "refresh@syndipro.qc", "password": "MotDePasse123!"},
    )
    assert resp.status_code == 200
    return resp.json()


def test_login_returns_access_and_refresh_tokens(client: TestClient):
    """Le login doit retourner access_token + refresh_token."""
    data = _register_and_login(client)
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    # Le refresh token doit être suffisamment long (opaque, non-JWT)
    assert len(data["refresh_token"]) >= 64


def test_refresh_returns_new_token_pair(client: TestClient):
    """POST /auth/refresh retourne une nouvelle paire access + refresh."""
    initial = _register_and_login(client)

    resp = client.post("/auth/refresh", json={"refresh_token": initial["refresh_token"]})
    assert resp.status_code == 200
    new_tokens = resp.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    # Le refresh token DOIT être différent (rotation) — c'est l'invariant de sécurité.
    # L'access_token JWT peut être identique si émis dans la même seconde (granularité exp).
    assert new_tokens["refresh_token"] != initial["refresh_token"]


def test_old_refresh_token_invalidated_after_use(client: TestClient):
    """Un refresh token déjà utilisé (rotation) doit être rejeté."""
    initial = _register_and_login(client)

    # Première utilisation — OK
    first_refresh = client.post("/auth/refresh", json={"refresh_token": initial["refresh_token"]})
    assert first_refresh.status_code == 200

    # Seconde utilisation du MÊME token — doit échouer
    second_refresh = client.post("/auth/refresh", json={"refresh_token": initial["refresh_token"]})
    assert second_refresh.status_code == 401
    assert "révoqué" in second_refresh.json()["detail"].lower()


def test_invalid_refresh_token_rejected(client: TestClient):
    """Un refresh token inexistant doit être rejeté en 401."""
    resp = client.post("/auth/refresh", json={"refresh_token": "un-token-qui-nexiste-pas-12345"})
    assert resp.status_code == 401
    assert "invalide" in resp.json()["detail"].lower()


def test_expired_refresh_token_rejected(client: TestClient, session: Session):
    """Un refresh token expiré doit être rejeté."""
    initial = _register_and_login(client)

    # Forcer l'expiration en manipulant la BDD
    token_hash = hash_refresh_token(initial["refresh_token"])
    record = session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()
    assert record is not None
    record.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    session.add(record)
    session.commit()

    resp = client.post("/auth/refresh", json={"refresh_token": initial["refresh_token"]})
    assert resp.status_code == 401
    assert "expiré" in resp.json()["detail"].lower()


def test_logout_revokes_refresh_token(client: TestClient):
    """POST /auth/logout révoque le refresh token."""
    initial = _register_and_login(client)

    logout_resp = client.post("/auth/logout", json={"refresh_token": initial["refresh_token"]})
    assert logout_resp.status_code == 204

    # Le refresh token ne doit plus fonctionner
    refresh_resp = client.post("/auth/refresh", json={"refresh_token": initial["refresh_token"]})
    assert refresh_resp.status_code == 401


def test_logout_with_invalid_token_silent(client: TestClient):
    """Le logout avec un token invalide ne révèle rien (silencieux)."""
    # Ne doit pas crasher ni révéler l'existence du token
    resp = client.post("/auth/logout", json={"refresh_token": "un-token-invalide"})
    assert resp.status_code == 204


def test_new_access_token_works_after_refresh(client: TestClient):
    """Le nouvel access token retourné par /refresh doit être utilisable."""
    initial = _register_and_login(client)
    refresh_resp = client.post("/auth/refresh", json={"refresh_token": initial["refresh_token"]})
    new_tokens = refresh_resp.json()

    # Utiliser le nouveau access token
    me_resp = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "refresh@syndipro.qc"


def test_refresh_chain_works_multiple_times(client: TestClient):
    """On peut enchaîner plusieurs refresh (toujours avec le dernier token)."""
    initial = _register_and_login(client)
    current = initial["refresh_token"]

    for _ in range(3):
        resp = client.post("/auth/refresh", json={"refresh_token": current})
        assert resp.status_code == 200
        current = resp.json()["refresh_token"]

    # Le dernier token fonctionne encore
    final = client.post("/auth/refresh", json={"refresh_token": current})
    assert final.status_code == 200
