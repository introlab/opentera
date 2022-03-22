"""create device site table

Revision ID: c08e332cdf5f
Revises: 28580f044a97
Create Date: 2022-03-01 13:29:43.443905

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence
import time


# revision identifiers, used by Alembic.
revision = 'c08e332cdf5f'
down_revision = '28580f044a97'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('t_devices_sites',
                    sa.Column('version_id', sa.BigInteger, nullable=False, default=time.time() * 1000),
                    sa.Column('id_device_site', sa.Integer, sa.Sequence('id_device_site_sequence'), primary_key=True,
                              autoincrement=True),
                    sa.Column('id_device', sa.Integer, sa.ForeignKey('t_devices.id_device', ondelete='cascade'),
                              nullable=False),
                    sa.Column('id_site', sa.Integer, sa.ForeignKey('t_sites.id_site', ondelete='cascade'),
                              nullable=False))
    op.execute(CreateSequence(sa.Sequence('id_device_site_sequence')))


def downgrade():
    op.drop_table('t_devices_sites')
