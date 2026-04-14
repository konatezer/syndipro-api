from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    response = client.post(
        "/auth/register",
        json={
            "email": "nouveau@syndipro.qc",
            "nom": "Lavoie",
            "prenom": "Marie",
            "password": "MotDePasse123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "nouveau@syndipro.qc"
    assert data["nom"] == "Lavoie"
    assert data["prenom"] == "Marie"
    assert data["role"] == "coproprietaire"
    assert "id" in data


def test_register_duplicate_email(client: TestClient):
    user_data = {
        "email": "dupe@syndipro.qc",
        "nom": "Gagnon",
        "prenom": "Pierre",
        "password": "MotDePasse123!",
    }
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert "existe déjà" in response.json()["detail"]


def test_login_success(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "login@syndipro.qc",
            "nom": "Roy",
            "prenom": "Luc",
            "password": "MotDePasse123!",
        },
    )
    response = client.post(
        "/auth/login",
        data={"username": "login@syndipro.qc", "password": "MotDePasse123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "wrong@syndipro.qc",
            "nom": "Morin",
            "prenom": "Sophie",
            "password": "MotDePasse123!",
        },
    )
    response = client.post(
        "/auth/login",
        data={"username": "wrong@syndipro.qc", "password": "MauvaisMotDePasse"},
    )
    assert response.status_code == 401


def test_get_me_authenticated(client: TestClient, auth_headers: dict):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@syndipro.qc"


def test_get_me_unauthenticated(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401
