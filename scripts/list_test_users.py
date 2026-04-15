"""
Script pour lister tous les comptes de test SyndiPro.

Usage:
    cd syndipro-api
    uv run python scripts/list_test_users.py
"""

from sqlmodel import Session, create_engine, select

from app.core.config import DATABASE_URL
from app.models.membre import MembreSyndicat
from app.models.syndicat import Syndicat
from app.models.user import User


def list_users():
    engine = create_engine(DATABASE_URL, echo=False)
    with Session(engine) as session:
        users = list(session.exec(select(User).order_by(User.email)).all())

        print("=" * 80)
        print("COMPTES DE TEST SYNDIPRO")
        print("=" * 80)
        print()
        print(f"Total : {len(users)} utilisateurs\n")

        # Admin principal
        admin = session.exec(
            select(User).where(User.email == "admin@syndipro.qc")
        ).first()
        if admin:
            print("🔑 COMPTE ADMIN PRINCIPAL (accès à tous les syndicats)")
            print("─" * 80)
            print(f"   Email    : admin@syndipro.qc")
            print(f"   Password : Admin123!")
            print(f"   Rôle     : gestionnaire")
            print()

        # Comptes de seed (emails @exemple.qc)
        test_users = [u for u in users if u.email.endswith("@exemple.qc")]
        if test_users:
            print(f"👥 COMPTES COPROPRIÉTAIRES / ADMIN CA ({len(test_users)} comptes)")
            print("   Tous avec le mot de passe : Test123!")
            print("─" * 80)
            for u in test_users[:10]:
                memberships = list(
                    session.exec(
                        select(MembreSyndicat).where(MembreSyndicat.user_id == u.id)
                    ).all()
                )
                syndicat_count = len(memberships)
                print(
                    f"   {u.email:<45} | {u.prenom} {u.nom:<15} | "
                    f"{u.role.value:<15} | {syndicat_count} syndicat(s)"
                )
            if len(test_users) > 10:
                print(f"   ... et {len(test_users) - 10} autres comptes")
            print()

        # Autres comptes
        autres = [
            u
            for u in users
            if not u.email.endswith("@exemple.qc") and u.email != "admin@syndipro.qc"
        ]
        if autres:
            print(f"📋 AUTRES COMPTES EXISTANTS ({len(autres)} comptes)")
            print("─" * 80)
            for u in autres:
                print(
                    f"   {u.email:<45} | {u.prenom} {u.nom:<15} | "
                    f"{u.role.value:<15}"
                )
            print()

        # Liste des syndicats
        syndicats = list(
            session.exec(select(Syndicat).order_by(Syndicat.nom)).all()
        )
        if syndicats:
            print(f"🏢 SYNDICATS DISPONIBLES ({len(syndicats)})")
            print("─" * 80)
            for s in syndicats:
                membres_count = len(
                    list(
                        session.exec(
                            select(MembreSyndicat).where(
                                MembreSyndicat.syndicat_id == s.id
                            )
                        ).all()
                    )
                )
                print(
                    f"   {s.nom:<40} | {s.ville:<12} | "
                    f"{s.nombre_unites:>4} unités | {membres_count} membres"
                )
            print()

        print("=" * 80)
        print("URLs DE CONNEXION")
        print("=" * 80)
        print("   Frontend : http://localhost:3000/login")
        print("   API Docs : http://localhost:8000/docs")
        print("=" * 80)


if __name__ == "__main__":
    list_users()
