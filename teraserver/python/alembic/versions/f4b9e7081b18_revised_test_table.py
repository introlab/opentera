"""revised test table

Revision ID: f4b9e7081b18
Revises: dbe0ef5395eb
Create Date: 2022-04-01 07:36:25.422384

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence
from sqlalchemy.engine.reflection import Inspector
import time

# revision identifiers, used by Alembic.
revision = 'f4b9e7081b18'
down_revision = 'dbe0ef5395eb'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 't_tests' in tables:
        op.drop_table('t_tests')
    
    op.execute(DropSequence(sa.Sequence('id_test_sequence')))

    op.create_table('t_tests',
                    sa.Column('version_id', sa.BigInteger, nullable=False, default=time.time() * 1000),
                    sa.Column('id_test', sa.Integer, sa.Sequence('id_test_sequence'), primary_key=True,
                              autoincrement=True),
                    sa.Column('id_test_type', sa.Integer, sa.ForeignKey('t_tests_types.id_test_type'), nullable=False),
                    sa.Column('id_session', sa.Integer, sa.ForeignKey('t_sessions.id_session', ondelete='cascade'),
                              nullable=False),
                    sa.Column('id_device', sa.Integer, sa.ForeignKey("t_devices.id_device"), nullable=True),
                    sa.Column('id_participant', sa.Integer, sa.ForeignKey("t_participants.id_participant"),
                              nullable=True),
                    sa.Column('id_user', sa.Integer, sa.ForeignKey("t_users.id_user"), nullable=True),
                    sa.Column('id_service', sa.Integer, sa.ForeignKey("t_services.id_service"), nullable=True),
                    sa.Column('test_uuid', sa.String(36), nullable=False, unique=True),
                    sa.Column('test_name', sa.String, nullable=False),
                    sa.Column('test_datetime', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('test_status', sa.Integer, nullable=False, default=0),
                    sa.Column('test_summary', sa.String, nullable=True)
                    )
    op.execute(CreateSequence(sa.Sequence('id_test_sequence')))


def downgrade():
    pass
