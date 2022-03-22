"""create service site table

Revision ID: 28580f044a97
Revises: 60f5b2ed8b5a
Create Date: 2022-02-24 08:31:01.673130

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence
import time


# revision identifiers, used by Alembic.
revision = '28580f044a97'
down_revision = '60f5b2ed8b5a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('t_services_sites',
                    sa.Column('version_id', sa.BigInteger, nullable=False, default=time.time() * 1000),
                    sa.Column('id_service_site', sa.Integer, sa.Sequence('id_service_site_sequence'), primary_key=True,
                              autoincrement=True),
                    sa.Column('id_service', sa.Integer, sa.ForeignKey('t_services.id_service', ondelete='cascade'),
                              nullable=False),
                    sa.Column('id_site', sa.Integer, sa.ForeignKey('t_sites.id_site', ondelete='cascade'),
                              nullable=False))
    op.execute(CreateSequence(sa.Sequence('id_service_site_sequence')))


def downgrade():
    op.drop_table('t_services_sites')
