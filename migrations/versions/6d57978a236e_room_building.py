"""Room building

Revision ID: 6d57978a236e
Revises: b0d96bbca3cd
Create Date: 2022-11-15 14:28:24.824017

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d57978a236e'
down_revision = 'b0d96bbca3cd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('room', sa.Column('building', sa.String(), nullable=True))


def downgrade():
    op.drop_column('room', 'building')
