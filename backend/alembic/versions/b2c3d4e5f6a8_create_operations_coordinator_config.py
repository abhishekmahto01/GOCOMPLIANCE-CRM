"""create_operations_coordinator_config_table

Revision ID: b2c3d4e5f6a8
Revises: a1b2c3d4e5f7
Create Date: 2026-10-09 01:00:00.000000

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a8"
down_revision: Union[str, None] = "a1b2c3d4e5f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create operations_coordinator_config table
    op.create_table(
        "operations_coordinator_config",
        sa.Column("config_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("company_master.company_id", ondelete="CASCADE", name="fk_ops_coord_cfg_company_id"),
            nullable=False,
        ),
        sa.Column(
            "coordinator_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("user_master.user_id", ondelete="SET NULL", name="fk_ops_coord_cfg_coordinator_user_id"),
            nullable=True,
        ),
        sa.Column(
            "updated_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("user_master.user_id", ondelete="SET NULL", name="fk_ops_coord_cfg_updated_by_user_id"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("company_id", name="uq_operations_coordinator_company_id"),
        comment="Configuration mapping Sales entry company to default Operations coordinator",
    )

    op.create_index(
        "ix_operations_coordinator_config_company_id",
        "operations_coordinator_config",
        ["company_id"],
    )
    op.create_index(
        "ix_operations_coordinator_config_coordinator_user_id",
        "operations_coordinator_config",
        ["coordinator_user_id"],
    )

    # 2. Seed initial default coordinator config for existing active companies mapping to Mansi Singhal (if present)
    bind = op.get_bind()
    mansi_row = bind.execute(
        sa.text("SELECT user_id FROM user_master WHERE employee_code = 'CG0003' OR LOWER(first_name) LIKE '%mansi%' LIMIT 1")
    ).fetchone()

    mansi_user_id = str(mansi_row[0]) if mansi_row else None

    company_rows = bind.execute(
        sa.text("SELECT company_id FROM company_master WHERE status = 'ACTIVE'")
    ).fetchall()

    for comp in company_rows:
        comp_id = str(comp[0])
        cfg_id = str(uuid.uuid4())
        bind.execute(
            sa.text(
                """
                INSERT INTO operations_coordinator_config (config_id, company_id, coordinator_user_id, created_at, updated_at)
                VALUES (:cfg_id, :comp_id, :coord_id, NOW(), NOW())
                ON CONFLICT (company_id) DO NOTHING
                """
            ),
            {"cfg_id": cfg_id, "comp_id": comp_id, "coord_id": mansi_user_id},
        )


def downgrade() -> None:
    op.drop_index("ix_operations_coordinator_config_coordinator_user_id", table_name="operations_coordinator_config")
    op.drop_index("ix_operations_coordinator_config_company_id", table_name="operations_coordinator_config")
    op.drop_table("operations_coordinator_config")
