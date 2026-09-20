"""add_credentials_initialized_at

Revision ID: 50c6c543b4db
Revises: 65ff8484468e
Create Date: 2026-09-21 01:34:00.015414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50c6c543b4db'
down_revision: Union[str, None] = '65ff8484468e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user_master',
        sa.Column(
            'credentials_initialized_at',
            sa.DateTime(timezone=True),
            nullable=True,
            comment='Timestamp when credentials were first provisioned (UTC)',
        ),
    )


def downgrade() -> None:
    op.drop_column('user_master', 'credentials_initialized_at')

