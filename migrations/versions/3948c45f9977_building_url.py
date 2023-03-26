"""Building url

Revision ID: 3948c45f9977
Revises: 63263ee9e08e
Create Date: 2023-03-20 16:42:54.345727

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '3948c45f9977'
down_revision = '63263ee9e08e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('room', sa.Column('building_url', sa.String(), nullable=True))


def downgrade():
    op.drop_column('room', 'building_url')
