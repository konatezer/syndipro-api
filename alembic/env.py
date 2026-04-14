import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

load_dotenv()

from sqlmodel import SQLModel  # noqa: E402

from app.models.assemblee import Assemblee, Resolution, Vote  # noqa: E402, F401
from app.models.communication import Annonce  # noqa: E402, F401
from app.models.finance import Cotisation, Depense, FondsPrevoyance  # noqa: E402, F401
from app.models.loi16 import ComposanteImmeuble, EntreeCarnet, ScoreConformite  # noqa: E402, F401
from app.models.maintenance import DemandeMaintenance, Document  # noqa: E402, F401
from app.models.membre import MembreSyndicat  # noqa: E402, F401
from app.models.syndicat import Syndicat  # noqa: E402, F401
from app.models.unite import Unite  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Injecte DATABASE_URL du .env dans la config Alembic
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLModel.metadata contient toutes les tables déclarées
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
