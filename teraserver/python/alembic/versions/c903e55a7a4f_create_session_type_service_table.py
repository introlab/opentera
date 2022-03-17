"""create session type service table

Revision ID: c903e55a7a4f
Revises: c08e332cdf5f
Create Date: 2022-03-08 08:19:11.841941

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence
import time


# revision identifiers, used by Alembic.
revision = 'c903e55a7a4f'
down_revision = 'c08e332cdf5f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('t_sessions_types_sites',
                    sa.Column('version_id', sa.BigInteger, nullable=False, default=time.time() * 1000),
                    sa.Column('id_session_type_site', sa.Integer, sa.Sequence('id_session_type_site_sequence'),
                              primary_key=True, autoincrement=True),
                    sa.Column('id_session_type', sa.Integer, sa.ForeignKey('t_sessions_types.id_session_type',
                                                                           ondelete='cascade'), nullable=False),
                    sa.Column('id_site', sa.Integer, sa.ForeignKey('t_sites.id_site', ondelete='cascade'),
                              nullable=False))
    op.execute(CreateSequence(sa.Sequence('id_session_type_site_sequence')))


def downgrade():
    op.drop_table('t_sessions_types_sites')
