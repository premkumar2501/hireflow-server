"""Create the users table with the full auth schema.

Revision ID: b977743df9e7
Revises:
Create Date: 2026-09-23 15:21:04.873072

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b977743df9e7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the users table with all registration fields used by the app."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "users" not in table_names:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("username", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("phoneNo", sa.String(), nullable=True),
            sa.Column("password", sa.String(), nullable=False),
            sa.Column("is_varify", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if "ix_users_username" not in [idx["name"] for idx in sa.inspect(bind).get_indexes("users")]:
        op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    if "ix_users_email" not in [idx["name"] for idx in sa.inspect(bind).get_indexes("users")]:
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    """Drop the users table."""
    op.drop_table("users", if_exists=True)
