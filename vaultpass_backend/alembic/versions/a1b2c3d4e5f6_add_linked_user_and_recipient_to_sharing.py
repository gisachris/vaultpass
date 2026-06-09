"""add_linked_user_and_recipient_to_sharing

Revision ID: a1b2c3d4e5f6
Revises: e5c1fa95eb0d
Create Date: 2026-06-09 19:11:00.000000

Adds:
  - trusted_contacts.linked_user_id  (nullable FK -> users.id, SET NULL on delete)
  - document_shares.recipient_user_id (nullable FK -> users.id, SET NULL on delete)

Both columns are nullable so all existing rows are unaffected.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "e5c1fa95eb0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── trusted_contacts.linked_user_id ──────────────────────────────── #
    op.add_column(
        "trusted_contacts",
        sa.Column(
            "linked_user_id",
            sa.UUID(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_trusted_contacts_linked_user_id",
        "trusted_contacts",
        "users",
        ["linked_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_trusted_contacts_linked_user_id",
        "trusted_contacts",
        ["linked_user_id"],
    )

    # ── document_shares.recipient_user_id ────────────────────────────── #
    op.add_column(
        "document_shares",
        sa.Column(
            "recipient_user_id",
            sa.UUID(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_document_shares_recipient_user_id",
        "document_shares",
        "users",
        ["recipient_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_document_shares_recipient_user_id",
        "document_shares",
        ["recipient_user_id"],
    )


def downgrade() -> None:
    # ── document_shares ──────────────────────────────────────────────── #
    op.drop_index("ix_document_shares_recipient_user_id", table_name="document_shares")
    op.drop_constraint(
        "fk_document_shares_recipient_user_id", "document_shares", type_="foreignkey"
    )
    op.drop_column("document_shares", "recipient_user_id")

    # ── trusted_contacts ─────────────────────────────────────────────── #
    op.drop_index("ix_trusted_contacts_linked_user_id", table_name="trusted_contacts")
    op.drop_constraint(
        "fk_trusted_contacts_linked_user_id", "trusted_contacts", type_="foreignkey"
    )
    op.drop_column("trusted_contacts", "linked_user_id")
