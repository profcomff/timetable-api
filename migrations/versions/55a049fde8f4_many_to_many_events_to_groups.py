"""Many to Many events to groups

Revision ID: 55a049fde8f4
Revises: fe04c8baa5ab
Create Date: 2023-07-02 22:58:17.045433

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '55a049fde8f4'
down_revision = 'fe04c8baa5ab'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'events_groups',
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['event_id'],
            ['event.id'],
        ),
        sa.ForeignKeyConstraint(
            ['group_id'],
            ['group.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('events_groups')
