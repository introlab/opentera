"""soft delete upgrade

Revision ID: 65a42f6ee567
Revises: f4b9e7081b18
Create Date: 2023-02-20 11:33:25.193275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65a42f6ee567'
down_revision = 'f4b9e7081b18'
branch_labels = None
depends_on = None


def upgrade():
    # Remove site_name unique constraint on t_sites
    op.drop_constraint(constraint_name='t_sites_site_name_key', table_name='t_sites', type_='unique')

    # TeraSessionParticipants.id_session add ondelete='cascade'
    op.drop_constraint(constraint_name='t_sessions_participants_id_session_fkey', table_name='t_sessions_participants',
                       type_='foreignkey')
    op.create_foreign_key(constraint_name=None, source_table='t_sessions_participants', referent_table='t_sessions',
                          remote_cols=['id_session'], local_cols=['id_session'], ondelete='cascade')

    # TeraUserUserGroup.id_user_group add ondelete=cascade
    op.drop_constraint(constraint_name='t_users_users_groups_id_user_group_fkey', table_name='t_users_users_groups',
                       type_='foreignkey')
    op.create_foreign_key(constraint_name=None, source_table='t_users_users_groups', referent_table='t_users_groups',
                          remote_cols=['id_user_group'], local_cols=['id_user_group'], ondelete='cascade')

    # TeraSession: id_creator_service - change "cascade set null" to "cascade delete"
    op.drop_constraint(constraint_name='t_sessions_id_creator_user_fkey', table_name='t_sessions', type_='foreignkey')
    op.create_foreign_key(constraint_name=None, source_table='t_sessions', referent_table='t_services',
                          remote_cols=['id_service'], local_cols=['id_creator_service'], ondelete='cascade')

    # Add soft delete columns to tables
    op.add_column('t_assets', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_devices', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_devices_participants', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_devices_projects', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_devices_sites', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_participants', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_participants_groups', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_projects', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_services', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_services_access', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_services_configs', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_services_configs_specifics', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_services_projects', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_services_roles', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_services_sites', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_sessions', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_sessions_devices', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_sessions_events', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_sessions_participants', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_sessions_types', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_sessions_types_projects', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_sessions_types_sites', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_sessions_users', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_sites', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_tests', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_tests_types', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_tests_types_projects', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_tests_types_sites', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_users', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_users_groups', sa.Column('deleted_at', sa.DateTime(timezone=True)))
    op.add_column('t_users_users_groups', sa.Column('deleted_at', sa.DateTime(timezone=True)))


def downgrade():
    # No downgrade possible from that even darker path...
    pass
