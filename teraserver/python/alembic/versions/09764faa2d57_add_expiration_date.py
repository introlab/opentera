"""add expiration date

Revision ID: 09764faa2d57
Revises: e6ee93ef205b
Create Date: 2024-04-03 17:06:05.108297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09764faa2d57'
down_revision = 'e6ee93ef205b'
branch_labels = None
depends_on = None


def upgrade():
    # Add asset_expiration_datetime column to t_assets table
    op.add_column(table_name='t_assets', column=sa.Column('asset_expiration_datetime',
                                                          sa.TIMESTAMP(timezone=True), nullable=True))


def downgrade():
    # No downgrade possible from that dark path...
    pass
