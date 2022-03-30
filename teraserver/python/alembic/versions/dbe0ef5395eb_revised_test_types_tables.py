"""revised test types tables

Revision ID: dbe0ef5395eb
Revises: c903e55a7a4f
Create Date: 2022-03-28 15:01:21.497534

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence
from sqlalchemy.engine.reflection import Inspector
import time


# revision identifiers, used by Alembic.
revision = 'dbe0ef5395eb'
down_revision = 'c903e55a7a4f'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 't_tests_types_projects' in tables:
        op.drop_table('t_tests_types_projects')

    if 't_tests' in tables:
        op.drop_table('t_tests')

    if 't_tests_types' in tables:
        op.drop_table('t_tests_types')

    op.execute(DropSequence(sa.Sequence('id_test_type_sequence')))

    op.create_table('t_tests_types',
                    sa.Column('version_id', sa.BigInteger, nullable=False, default=time.time() * 1000),
                    sa.Column('id_test_type', sa.Integer, sa.Sequence('id_test_type_sequence'),
                              primary_key=True, autoincrement=True),
                    sa.Column('id_service', sa.Integer, sa.ForeignKey('t_services.id_service', ondelete='cascade'),
                              nullable=False),
                    sa.Column('test_type_uuid', sa.String(36), nullable=False, unique=True),
                    sa.Column('test_type_name', sa.String, nullable=False, unique=False),
                    sa.Column('test_type_description', sa.String, nullable=True),
                    sa.Column('test_type_has_json_format', sa.Boolean, nullable=False, default=False),
                    sa.Column('test_type_has_web_format', sa.Boolean, nullable=False, default=False),
                    sa.Column('test_type_has_web_editor', sa.Boolean, nullable=False, default=False)
                    )
    op.execute(CreateSequence(sa.Sequence('id_test_type_sequence')))

    op.create_table('t_tests_types_sites',
                    sa.Column('version_id', sa.BigInteger, nullable=False, default=time.time() * 1000),
                    sa.Column('id_test_type_site', sa.Integer, sa.Sequence('id_test_type_site_sequence'),
                              primary_key=True, autoincrement=True),
                    sa.Column('id_test_type', sa.Integer, sa.ForeignKey('t_tests_types.id_test_type',
                                                                        ondelete='cascade'), nullable=False),
                    sa.Column('id_site', sa.Integer, sa.ForeignKey('t_sites.id_site', ondelete='cascade'),
                              nullable=False))
    op.execute(CreateSequence(sa.Sequence('id_test_type_site_sequence')))

    op.create_table('t_tests_types_projects',
                    sa.Column('version_id', sa.BigInteger, nullable=False, default=time.time() * 1000),
                    sa.Column('id_test_type_project', sa.Integer, sa.Sequence('id_test_type_project_sequence'),
                              primary_key=True, autoincrement=True),
                    sa.Column('id_test_type', sa.Integer, sa.ForeignKey('t_tests_types.id_test_type',
                                                                        ondelete='cascade'), nullable=False),
                    sa.Column('id_project', sa.Integer, sa.ForeignKey('t_projects.id_project', ondelete='cascade'),
                              nullable=False))
    op.execute(CreateSequence(sa.Sequence('id_test_type_project_sequence')))


def downgrade():
    # No way to downgrade...
    pass
