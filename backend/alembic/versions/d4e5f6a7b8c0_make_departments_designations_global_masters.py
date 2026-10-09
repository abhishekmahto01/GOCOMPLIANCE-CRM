"""make_departments_designations_global_masters

Revision ID: d4e5f6a7b8c0
Revises: c3d4e5f6a7b9
Create Date: 2026-10-10 02:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c0"
down_revision: Union[str, None] = "c3d4e5f6a7b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Deduplicate departments before dropping company_id:
    # If any duplicate codes exist across companies, remap users to the canonical department record.
    conn.execute(sa.text("""
        DO $$
        DECLARE
            r RECORD;
            canonical_id UUID;
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'department_master'
            ) THEN
                FOR r IN SELECT DISTINCT UPPER(department_code) AS dcode FROM department_master LOOP
                    -- Pick canonical department (earliest created or first by id)
                    SELECT department_id INTO canonical_id 
                    FROM department_master 
                    WHERE UPPER(department_code) = r.dcode 
                    ORDER BY created_at ASC, department_id ASC 
                    LIMIT 1;

                    -- Update users pointing to any other duplicate ID
                    UPDATE user_master 
                    SET department_id = canonical_id 
                    WHERE department_id IN (
                        SELECT department_id FROM department_master 
                        WHERE UPPER(department_code) = r.dcode AND department_id != canonical_id
                    );

                    -- Delete duplicate department records
                    DELETE FROM department_master 
                    WHERE UPPER(department_code) = r.dcode AND department_id != canonical_id;
                END LOOP;
            END IF;
        END $$;
    """))

    # 2. Deduplicate designations before dropping company_id:
    # If any duplicate codes exist across companies, remap users to the canonical designation record.
    conn.execute(sa.text("""
        DO $$
        DECLARE
            r RECORD;
            canonical_id UUID;
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'designation_master'
            ) THEN
                FOR r IN SELECT DISTINCT UPPER(designation_code) AS dcode FROM designation_master LOOP
                    -- Pick canonical designation (earliest created or first by id)
                    SELECT designation_id INTO canonical_id 
                    FROM designation_master 
                    WHERE UPPER(designation_code) = r.dcode 
                    ORDER BY created_at ASC, designation_id ASC 
                    LIMIT 1;

                    -- Update users pointing to any other duplicate ID
                    UPDATE user_master 
                    SET designation_id = canonical_id 
                    WHERE designation_id IN (
                        SELECT designation_id FROM designation_master 
                        WHERE UPPER(designation_code) = r.dcode AND designation_id != canonical_id
                    );

                    -- Delete duplicate designation records
                    DELETE FROM designation_master 
                    WHERE UPPER(designation_code) = r.dcode AND designation_id != canonical_id;
                END LOOP;
            END IF;
        END $$;
    """))

    # 3. Drop foreign keys and index on company_id for department_master if they exist
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_department_company_id' AND table_name = 'department_master'
            ) THEN
                ALTER TABLE department_master DROP CONSTRAINT fk_department_company_id;
            END IF;
        END $$;
    """))

    conn.execute(sa.text("""
        DROP INDEX IF EXISTS ix_department_master_company_id;
    """))

    # Drop company_id column from department_master if exists
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'department_master' AND column_name = 'company_id'
            ) THEN
                ALTER TABLE department_master DROP COLUMN company_id;
            END IF;
        END $$;
    """))

    # 4. Drop foreign keys and index on company_id for designation_master if they exist
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_designation_company_id' AND table_name = 'designation_master'
            ) THEN
                ALTER TABLE designation_master DROP CONSTRAINT fk_designation_company_id;
            END IF;
        END $$;
    """))

    conn.execute(sa.text("""
        DROP INDEX IF EXISTS ix_designation_master_company_id;
    """))

    # Drop company_id column from designation_master if exists
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'designation_master' AND column_name = 'company_id'
            ) THEN
                ALTER TABLE designation_master DROP COLUMN company_id;
            END IF;
        END $$;
    """))

    # 5. Ensure global unique constraints exist on department_code, department_name, designation_code, designation_name
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'uq_department_code' AND table_name = 'department_master'
            ) THEN
                ALTER TABLE department_master ADD CONSTRAINT uq_department_code UNIQUE (department_code);
            END IF;
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'uq_department_name' AND table_name = 'department_master'
            ) THEN
                ALTER TABLE department_master ADD CONSTRAINT uq_department_name UNIQUE (department_name);
            END IF;
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'uq_designation_code' AND table_name = 'designation_master'
            ) THEN
                ALTER TABLE designation_master ADD CONSTRAINT uq_designation_code UNIQUE (designation_code);
            END IF;
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'uq_designation_name' AND table_name = 'designation_master'
            ) THEN
                ALTER TABLE designation_master ADD CONSTRAINT uq_designation_name UNIQUE (designation_name);
            END IF;
        END $$;
    """))


def downgrade() -> None:
    # Re-add nullable company_id column to department_master
    op.add_column(
        "department_master",
        sa.Column("company_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_department_company_id",
        "department_master",
        "company_master",
        ["company_id"],
        ["company_id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_department_master_company_id", "department_master", ["company_id"])

    # Re-add nullable company_id column to designation_master
    op.add_column(
        "designation_master",
        sa.Column("company_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_designation_company_id",
        "designation_master",
        "company_master",
        ["company_id"],
        ["company_id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_designation_master_company_id", "designation_master", ["company_id"])
