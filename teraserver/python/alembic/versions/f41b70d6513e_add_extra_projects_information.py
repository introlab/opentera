"""Add extra projects information

Revision ID: f41b70d6513e
Revises: 65a42f6ee567
Create Date: 2023-05-02 10:04:28.233886

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f41b70d6513e'
down_revision = '65a42f6ee567'
branch_labels = None
depends_on = None


def upgrade():
    # Add extra project informations
    op.add_column('t_projects', sa.Column('project_enabled', sa.Boolean, nullable=False, server_default=str(True)))
    op.add_column('t_projects', sa.Column('project_description', sa.String, nullable=True))


def downgrade():
    # At last, a path back to the light!
    op.drop_column('t_projects', 'project_enabled')
    op.drop_column('t_projects', 'project_description')
