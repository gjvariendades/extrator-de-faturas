"""fix users email uniqueness scope per tenant

Revision ID: 20240623_000003
Revises: 20240622_000002
Create Date: 2024-06-23 00:00:03
"""

from alembic import op


revision = "20240623_000003"
down_revision = "20240622_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove global uniqueness on users.email (legacy from initial migration)
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_key")


def downgrade() -> None:
    op.execute("ALTER TABLE users ADD CONSTRAINT users_email_key UNIQUE (email)")
