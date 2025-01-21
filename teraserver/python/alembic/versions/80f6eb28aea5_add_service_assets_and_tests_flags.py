"""add service assets and tests flags

Revision ID: 80f6eb28aea5
Revises: c58727df3ac2
Create Date: 2024-11-13 15:03:36.228009

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '80f6eb28aea5'
down_revision = 'c58727df3ac2'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns
    op.add_column(table_name='t_services', column=sa.Column('service_has_assets',
                                                            sa.Boolean, nullable=False, server_default=str(False)))

    op.add_column(table_name='t_services', column=sa.Column('service_has_tests',
                                                            sa.Boolean, nullable=False, server_default=str(False)))


def downgrade():
    # Remove columns
    op.drop_column('t_services', 'service_has_assets')
    op.drop_column('t_services', 'service_has_tests')
