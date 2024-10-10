"""assets table rework

Revision ID: 60f5b2ed8b5a
Revises: 
Create Date: 2022-01-31 08:13:24.214998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60f5b2ed8b5a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Change t_assets column asset_type to string - integers values should be converted directly in Postgresql
    op.alter_column(table_name='t_assets', column_name='asset_type', type=sa.String)

    # Change all current values to "application/octet-stream" since that is what we have right now
    op.execute("UPDATE t_assets SET asset_type=\'application/octet-stream\'")

    # Add asset datetime column
    op.add_column(table_name='t_assets', column=sa.Column('asset_datetime', sa.TIMESTAMP(timezone=True), nullable=True))

    # Add id_service column
    op.add_column(table_name='t_assets', column=sa.Column('id_service', sa.Integer,
                                                          sa.ForeignKey("t_services.id_service"), nullable=True))

    # Add foreign key constraint to asset service creator
    op.create_foreign_key(constraint_name=None, source_table='t_assets', referent_table='t_services',
                          local_cols=['asset_service_uuid'], remote_cols=['service_uuid'], ondelete='cascade')


def downgrade():
    # No downgrade possible from that dark path...
    pass
