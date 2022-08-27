"""Refactoring

Revision ID: e111af54f4bb
Revises: 0929a0a9586e
Create Date: 2022-08-27 06:15:13.630661

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e111af54f4bb'
down_revision = '0929a0a9586e'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('comments_lecturer', 'comment_lecturer')
    op.rename_table('lesson', 'event')
    op.rename_table('comments_lesson', 'comment_event')
    op.rename_table('lessons_lecturers', 'events_lecturers')
    op.rename_table('lessons_rooms', 'events_rooms')
    op.alter_column('comment_event', 'lesson_id', new_column_name='event_id')
    op.alter_column('events_lecturers', 'lesson_id', new_column_name='event_id')
    op.alter_column('events_rooms', 'lesson_id', new_column_name='event_id')


def downgrade():
    op.rename_table('comment_lecturer', 'comments_lecturer')
    op.rename_table('event', 'lesson')
    op.rename_table('comment_event', 'comments_lesson')
    op.rename_table('events_lecturers', 'lessons_lecturers')
    op.rename_table('events_rooms', 'lessons_rooms')
    op.alter_column('comment_event', 'event_id', new_column_name='lesson_id')
    op.alter_column('events_lecturers', 'event_id', new_column_name='lesson_id')
    op.alter_column('events_rooms', 'event_id', new_column_name='lesson_id')
