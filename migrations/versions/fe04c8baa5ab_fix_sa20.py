"""Fix sa20

Revision ID: fe04c8baa5ab
Revises: 3948c45f9977
Create Date: 2023-03-20 18:10:29.098467

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fe04c8baa5ab'
down_revision = '3948c45f9977'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('comment_event', 'event_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('comment_event', 'create_ts', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('comment_event', 'update_ts', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('comment_event', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column('comment_lecturer', 'lecturer_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('comment_lecturer', 'create_ts', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('comment_lecturer', 'update_ts', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('comment_lecturer', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column('event', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column('events_lecturers', 'event_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('events_lecturers', 'lecturer_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('events_rooms', 'event_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('events_rooms', 'room_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('group', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column('lecturer', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column('photo', 'lecturer_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('photo', 'link', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('photo', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column('room', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=False)


def downgrade():
    op.alter_column('room', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column('photo', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column('photo', 'link', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column('photo', 'lecturer_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('lecturer', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column('group', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column('events_rooms', 'room_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('events_rooms', 'event_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('events_lecturers', 'lecturer_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('events_lecturers', 'event_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('event', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column('comment_lecturer', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column('comment_lecturer', 'update_ts', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('comment_lecturer', 'create_ts', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('comment_lecturer', 'lecturer_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('comment_event', 'is_deleted', existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column('comment_event', 'update_ts', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('comment_event', 'create_ts', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('comment_event', 'event_id', existing_type=sa.INTEGER(), nullable=True)
