"""add_site_2fa_required_column_to_tera_site

Revision ID: c58727df3ac2
Revises: 89343f5c95b9
Create Date: 2024-09-30 13:58:38.839824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c58727df3ac2'
down_revision = '89343f5c95b9'
branch_labels = None
depends_on = None


def upgrade():
    # Add site_2fa_required column to t_sites table
    op.add_column(table_name='t_sites', column=sa.Column('site_2fa_required',
                                                         sa.Boolean, nullable=False, server_default=str(False)))

def downgrade():
    # Remove columns
    op.drop_column('t_sites', 'site_2fa_required')
