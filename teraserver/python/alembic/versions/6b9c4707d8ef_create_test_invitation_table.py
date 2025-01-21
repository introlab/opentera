"""create test invitation table

Revision ID: 6b9c4707d8ef
Revises: 818356b801fd
Create Date: 2024-12-11 10:40:52.393618

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence
import time
import datetime
from datetime import timezone

# revision identifiers, used by Alembic.
revision = '6b9c4707d8ef'
down_revision = '818356b801fd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('t_tests_invitations',
                    sa.Column('version_id', sa.BigInteger, nullable=False, default=time.time() * 1000),
                    sa.Column('id_test_invitation', sa.Integer, sa.Sequence('id_test_invitation_sequence'),
                              primary_key=True, autoincrement=True),
                    sa.Column('id_test_type', sa.Integer, sa.ForeignKey("t_tests_types.id_test_type",
                                                                        ondelete='cascade'), nullable=False),
                    sa.Column('id_session', sa.Integer, sa.ForeignKey("t_sessions.id_session",
                                                                      ondelete='cascade'), nullable=True),
                    sa.Column('id_user', sa.Integer, sa.ForeignKey("t_users.id_user",
                                                                   ondelete='cascade'), nullable=True),
                    sa.Column('id_participant', sa.Integer, sa.ForeignKey("t_participants.id_participant",
                                                                         ondelete='cascade'), nullable=True),
                    sa.Column('id_device', sa.Integer, sa.ForeignKey("t_devices.id_device",
                                                                     ondelete='cascade'), nullable=True),
                    sa.Column('id_project', sa.Integer, sa.ForeignKey("t_projects.id_project",
                                                                      ondelete='cascade'), nullable=False),
                    sa.Column('test_invitation_key', sa.String(16), nullable=False, unique=True),
                    sa.Column('test_invitation_max_count', sa.Integer, nullable=False, default=1),
                    sa.Column('test_invitation_count', sa.Integer, nullable=False, default=0),
                    sa.Column('test_invitation_creation_date', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('test_invitation_expiration_date', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('test_invitation_message', sa.String, nullable=True),
                    sa.Column('deleted_at', sa.DateTime(timezone=True)))

    op.execute(CreateSequence(sa.Sequence('id_test_invitation_sequence')))


def downgrade():
    op.drop_table('t_tests_invitations')
