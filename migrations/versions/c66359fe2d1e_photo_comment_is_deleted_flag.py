"""photo, comment, is_deleted flag

Revision ID: c66359fe2d1e
Revises: d6f98271bc6b
Create Date: 2022-08-25 21:14:35.470992

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c66359fe2d1e'
down_revision = 'd6f98271bc6b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'photo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lecturer_id', sa.Integer(), nullable=True),
        sa.Column('link', sa.String(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ['lecturer_id'],
            ['lecturer.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('link'),
    )
    op.create_table(
        'comments_lecturer',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lecturer_id', sa.Integer(), nullable=True),
        sa.Column('author_name', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('create_ts', sa.DateTime(), nullable=True),
        sa.Column('update_ts', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ['lecturer_id'],
            ['lecturer.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'comments_lesson',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=True),
        sa.Column('author_name', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('create_ts', sa.DateTime(), nullable=True),
        sa.Column('update_ts', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ['lesson_id'],
            ['lesson.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.add_column('group', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.add_column('lecturer', sa.Column('avatar_id', sa.Integer(), nullable=True))
    op.add_column('lecturer', sa.Column('avatar_link', sa.String(), nullable=True))
    op.add_column('lecturer', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('lecturer', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.create_foreign_key(None, 'lecturer', 'photo', ['avatar_link'], ['link'])
    op.create_foreign_key(None, 'lecturer', 'photo', ['avatar_id'], ['id'])
    op.add_column('lesson', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.add_column('room', sa.Column('is_deleted', sa.Boolean(), nullable=True))


def downgrade():
    op.execute('DELETE FROM "room" WHERE is_deleted;')
    op.execute('DELETE FROM "lesson" WHERE is_deleted;')
    op.execute('DELETE FROM "lecturer" WHERE is_deleted;')
    op.execute('DELETE FROM "group" WHERE is_deleted;')
    op.drop_column('room', 'is_deleted')
    op.drop_column('lesson', 'is_deleted')
    op.drop_constraint(None, 'lecturer', type_='foreignkey')
    op.drop_constraint(None, 'lecturer', type_='foreignkey')
    op.drop_column('lecturer', 'is_deleted')
    op.drop_column('lecturer', 'description')
    op.drop_column('lecturer', 'avatar_link')
    op.drop_column('lecturer', 'avatar_id')
    op.drop_column('group', 'is_deleted')
    op.drop_table('comments_lesson')
    op.drop_table('comments_lecturer')
    op.drop_table('photo')
