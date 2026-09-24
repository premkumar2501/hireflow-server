"""Repair the users table so registration data is stored properly.

Revision ID: d6d4d0d7a6d1
Revises: b977743df9e7
Create Date: 2026-09-24 08:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d6d4d0d7a6d1"
down_revision: Union[str, Sequence[str], None] = "b977743df9e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the missing fields required by the user model and registration flow."""
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

    columns = {column["name"] for column in inspector.get_columns("users")}
    indexes = {index["name"] for index in inspector.get_indexes("users")}

    if "password" not in columns:
        op.add_column("users", sa.Column("password", sa.String(), nullable=True))
    if "phoneNo" not in columns:
        op.add_column("users", sa.Column("phoneNo", sa.String(), nullable=True))
    if "is_varify" not in columns:
        op.add_column("users", sa.Column("is_varify", sa.Boolean(), nullable=True, server_default=sa.text("false")))
    if "created_at" not in columns:
        op.add_column("users", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))
    if "updated_at" not in columns:
        op.add_column("users", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))

    op.execute("UPDATE users SET password = '' WHERE password IS NULL")
    op.execute("UPDATE users SET is_varify = false WHERE is_varify IS NULL")

    op.alter_column("users", "password", existing_type=sa.String(), nullable=False)
    op.alter_column("users", "is_varify", existing_type=sa.Boolean(), nullable=False)

    if "ix_users_username" not in indexes:
        op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    if "ix_users_email" not in indexes:
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    """Remove the nonessential auth fields added by this migration."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    for column_name in ["phoneNo", "password", "is_varify", "created_at", "updated_at"]:
        if column_name in columns:
            op.drop_column("users", column_name)
