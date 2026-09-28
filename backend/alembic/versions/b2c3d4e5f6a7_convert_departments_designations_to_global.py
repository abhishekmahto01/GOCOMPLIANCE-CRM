"""convert_departments_designations_to_global

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-29 01:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Deduplicate departments: Remap users referencing duplicate departments to canonical department
    conn.execute(sa.text("""
        DO $$
        DECLARE
            r RECORD;
            canonical_id UUID;
        BEGIN
            FOR r IN SELECT DISTINCT UPPER(department_code) AS dcode FROM department_master LOOP
                -- Pick canonical department
                SELECT department_id INTO canonical_id 
                FROM department_master 
                WHERE UPPER(department_code) = r.dcode 
                ORDER BY created_at ASC 
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
        END $$;
    """))

    # 2. Deduplicate designations: Remap users referencing duplicate designations to canonical designation
    conn.execute(sa.text("""
        DO $$
        DECLARE
            r RECORD;
            canonical_id UUID;
        BEGIN
            FOR r IN SELECT DISTINCT UPPER(designation_code) AS dcode FROM designation_master LOOP
                -- Pick canonical designation
                SELECT designation_id INTO canonical_id 
                FROM designation_master 
                WHERE UPPER(designation_code) = r.dcode 
                ORDER BY created_at ASC 
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
        END $$;
    """))

    # 3. Alter Department Master schema to be global
    op.alter_column('department_master', 'company_id', nullable=True)
    op.drop_constraint('uq_department_company_code', 'department_master', type_='unique')
    op.drop_constraint('uq_department_company_name', 'department_master', type_='unique')
    op.create_unique_constraint('uq_department_code', 'department_master', ['department_code'])
    op.create_unique_constraint('uq_department_name', 'department_master', ['department_name'])

    # 4. Alter Designation Master schema to be global
    op.alter_column('designation_master', 'company_id', nullable=True)
    op.drop_constraint('uq_designation_company_code', 'designation_master', type_='unique')
    op.drop_constraint('uq_designation_company_name', 'designation_master', type_='unique')
    op.create_unique_constraint('uq_designation_code', 'designation_master', ['designation_code'])
    op.create_unique_constraint('uq_designation_name', 'designation_master', ['designation_name'])


def downgrade() -> None:
    op.drop_constraint('uq_designation_name', 'designation_master', type_='unique')
    op.drop_constraint('uq_designation_code', 'designation_master', type_='unique')
    op.create_unique_constraint('uq_designation_company_name', 'designation_master', ['company_id', 'designation_name'])
    op.create_unique_constraint('uq_designation_company_code', 'designation_master', ['company_id', 'designation_code'])
    op.alter_column('designation_master', 'company_id', nullable=False)

    op.drop_constraint('uq_department_name', 'department_master', type_='unique')
    op.drop_constraint('uq_department_code', 'department_master', type_='unique')
    op.create_unique_constraint('uq_department_company_name', 'department_master', ['company_id', 'department_name'])
    op.create_unique_constraint('uq_department_company_code', 'department_master', ['company_id', 'department_code'])
    op.alter_column('department_master', 'company_id', nullable=False)
