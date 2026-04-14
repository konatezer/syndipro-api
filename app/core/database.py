# app/core/database.py
from sqlmodel import SQLModel, Session, create_engine
from app.core.config import DATABASE_URL

# Crée le moteur de connexion à la BDD
# echo=True affiche les requêtes SQL (utile en dev)
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Crée toutes les tables au démarrage"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Fournit une session BDD pour chaque requête API"""
    with Session(engine) as session:
        yield session