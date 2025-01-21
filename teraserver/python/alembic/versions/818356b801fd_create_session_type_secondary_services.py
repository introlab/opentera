"""create session type secondary services

Revision ID: 818356b801fd
Revises: 80f6eb28aea5
Create Date: 2024-12-02 14:33:01.899045

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence
import time


# revision identifiers, used by Alembic.
revision = '818356b801fd'
down_revision = '80f6eb28aea5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('t_sessions_types_services',
                    sa.Column('version_id', sa.BigInteger, nullable=False, default=time.time() * 1000),
                    sa.Column('id_session_type_service', sa.Integer, sa.Sequence('id_session_type_service_sequence'),
                              primary_key=True, autoincrement=True),
                    sa.Column('id_session_type', sa.Integer, sa.ForeignKey('t_sessions_types.id_session_type',
                                                                           ondelete='cascade'), nullable=False),
                    sa.Column('id_service', sa.Integer, sa.ForeignKey('t_services.id_service',
                                                                      ondelete='cascade'), nullable=False),
                    sa.Column('deleted_at', sa.DateTime(timezone=True)))

    op.execute(CreateSequence(sa.Sequence('id_session_type_service_sequence')))


def downgrade():
    op.drop_table('t_sessions_types_services')
