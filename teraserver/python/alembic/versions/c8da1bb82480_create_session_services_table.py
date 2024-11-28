"""create_session_services_table

Revision ID: c8da1bb82480
Revises: 80f6eb28aea5
Create Date: 2024-11-28 16:05:56.924885

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence
import time


# revision identifiers, used by Alembic.
revision = 'c8da1bb82480'
down_revision = '80f6eb28aea5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('t_sessions_services',
                sa.Column('version_id', sa.BigInteger, nullable=False, default=time.time() * 1000),
                sa.Column('id_session_service', sa.Integer, sa.Sequence('id_session_service_sequence'),
                            primary_key=True, autoincrement=True),
                sa.Column('id_session', sa.Integer, sa.ForeignKey('t_sessions.id_session', ondelete='cascade'),
                          nullable=False),
                sa.Column('id_service', sa.Integer, sa.ForeignKey('t_services.id_service', ondelete='cascade'),
                          nullable=False))
    op.execute(CreateSequence(sa.Sequence('id_session_service_sequence')))


def downgrade():
    op.drop_table('t_sessions_services')
