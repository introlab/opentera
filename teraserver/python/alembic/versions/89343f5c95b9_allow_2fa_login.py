"""allow 2fa login

Revision ID: 89343f5c95b9
Revises: 09764faa2d57
Create Date: 2024-09-05 14:49:04.781595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89343f5c95b9'
down_revision = '09764faa2d57'
branch_labels = None
depends_on = None


def upgrade():
    # Add 2fa_enabled column to t_users table
    op.add_column(table_name='t_users', column=sa.Column('user_2fa_enabled',
                                                         sa.Boolean, nullable=False, server_default=str(False)))

    # Add 2fa_otp_enabled column to t_users table
    op.add_column(table_name='t_users', column=sa.Column('user_2fa_otp_enabled',
                                                         sa.Boolean, nullable=False, server_default=str(False)))

    # Add 2fa_email_enabled_column to t_users table
    # Will user user_email as 2fa email
    op.add_column(table_name='t_users', column=sa.Column('user_2fa_email_enabled',
                                                         sa.Boolean, nullable=False, server_default=str(False)))

    # Add 2fa_otp_secret column to t_users table
    # Secrets will be generated with pytop.random_base32()
    op.add_column(table_name='t_users', column=sa.Column('user_2fa_otp_secret',
                                                         sa.String(32), nullable=True))

    # Add a force_password_change column to t_users table
    op.add_column(table_name='t_users', column=sa.Column('user_force_password_change',
                                                         sa.Boolean, nullable=False, server_default=str(False)))


def downgrade():
    # Remove columns
    op.drop_column('t_users', 'user_2fa_enabled')
    op.drop_column('t_users', 'user_2fa_otp_enabled')
    op.drop_column('t_users', 'user_2fa_email_enabled')
    op.drop_column('t_users', 'user_2fa_otp_secret')
    op.drop_column('t_users', 'user_force_password_change')

