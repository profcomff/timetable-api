"""Many to many events to rooms and lecturers

Revision ID: 8bae03e22feb
Revises: 93612883178c
Create Date: 2022-08-19 03:29:18.184129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bae03e22feb'
down_revision = '93612883178c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'lessons_lecturers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=True),
        sa.Column('lecturer_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['lecturer_id'],
            ['lecturer.id'],
        ),
        sa.ForeignKeyConstraint(
            ['lesson_id'],
            ['lesson.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'lessons_rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=True),
        sa.Column('room_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['lesson_id'],
            ['lesson.id'],
        ),
        sa.ForeignKeyConstraint(
            ['room_id'],
            ['room.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.drop_constraint('lesson_room_id_fkey', 'lesson', type_='foreignkey')
    op.drop_constraint('lesson_lecturer_id_fkey', 'lesson', type_='foreignkey')
    op.drop_column('lesson', 'lecturer_id')
    op.drop_column('lesson', 'room_id')


def downgrade():
    op.add_column('lesson', sa.Column('room_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('lesson', sa.Column('lecturer_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('lesson_lecturer_id_fkey', 'lesson', 'lecturer', ['lecturer_id'], ['id'])
    op.create_foreign_key('lesson_room_id_fkey', 'lesson', 'room', ['room_id'], ['id'])
    op.drop_table('lessons_rooms')
    op.drop_table('lessons_lecturers')
