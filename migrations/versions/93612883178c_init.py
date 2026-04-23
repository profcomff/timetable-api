"""Init

Revision ID: 93612883178c
Revises:
Create Date: 2022-08-17 15:40:32.047879

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '93612883178c'
down_revision = None
branch_labels = None
depends_on = None

directions = sa.Enum('North', 'South', name='Directions')


def upgrade():
    op.create_table(
        'credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('scope', sa.JSON(), nullable=False),
        sa.Column('token', sa.JSON(), nullable=False),
        sa.Column('create_ts', sa.DateTime(), nullable=False),
        sa.Column('update_ts', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('number', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('number'),
    )
    op.create_table(
        'lecturer',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('middle_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'room',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('direction', directions, nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'lesson',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('lecturer_id', sa.Integer(), nullable=True),
        sa.Column('start_ts', sa.DateTime(), nullable=False),
        sa.Column('end_ts', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['group_id'],
            ['group.id'],
        ),
        sa.ForeignKeyConstraint(
            ['lecturer_id'],
            ['lecturer.id'],
        ),
        sa.ForeignKeyConstraint(
            ['room_id'],
            ['room.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('lesson')
    op.drop_table('room')
    op.drop_table('lecturer')
    op.drop_table('group')
    op.drop_table('credentials')
    directions.drop(op.get_bind(), checkfirst=True)
