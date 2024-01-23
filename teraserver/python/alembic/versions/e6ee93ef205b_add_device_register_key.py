"""Add device register key

Revision ID: e6ee93ef205b
Revises: f41b70d6513e
Create Date: 2024-01-23 08:15:07.224075

"""
from opentera.db.models.TeraServerSettings import TeraServerSettings


# revision identifiers, used by Alembic.
revision = 'e6ee93ef205b'
down_revision = 'f41b70d6513e'
branch_labels = None
depends_on = None


def upgrade():
    TeraServerSettings.set_server_setting(TeraServerSettings.ServerDeviceRegisterKey,
                                          TeraServerSettings.generate_token_key(10))


def downgrade():
    pass
