"""add refresh_tokens table

Revision ID: 4429135369d0
Revises: e92c9cca426f
Create Date: 2026-04-15 14:09:00.878015

Note: les autres tables (syndicats, unites, finances, etc.) ont été créées
via SQLModel.metadata.create_all() dans le script de seed. Cette migration
ne gère que refresh_tokens qui a été ajouté après le seed initial.
"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4429135369d0"
down_revision: Union[str, Sequence[str], None] = "e92c9cca426f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crée la table refresh_tokens pour le flux OAuth2 refresh + rotation."""
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "token_hash",
            sqlmodel.sql.sqltypes.AutoString(length=128),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_refresh_tokens_token_hash"),
        "refresh_tokens",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        op.f("ix_refresh_tokens_user_id"),
        "refresh_tokens",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Supprime la table refresh_tokens."""
    op.drop_index(op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_token_hash"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
