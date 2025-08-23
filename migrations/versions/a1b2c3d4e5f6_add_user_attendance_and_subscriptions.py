"""Add user attendance and subscription models

Revision ID: a1b2c3d4e5f6
Revises: fe04c8baa5ab
Create Date: 2024-08-23 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'fe04c8baa5ab'
branch_labels = None
depends_on = None


def upgrade():
    # Add new fields to event table
    op.add_column('event', sa.Column('creator_user_id', sa.Integer(), nullable=True))
    op.add_column('event', sa.Column('is_personal', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index(op.f('ix_event_creator_user_id'), 'event', ['creator_user_id'], unique=False)

    # Create user_event_attendance table
    op.create_table(
        'user_event_attendance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('attending', 'not_attending', 'maybe', name='attendancestatus'), nullable=False),
        sa.Column('create_ts', sa.DateTime(), nullable=False),
        sa.Column('update_ts', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_event_attendance_user_id'), 'user_event_attendance', ['user_id'], unique=False)

    # Create user_calendar_subscription table
    op.create_table(
        'user_calendar_subscription',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subscription_type', sa.Enum('group', 'lecturer', 'room', name='subscriptiontype'), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('create_ts', sa.DateTime(), nullable=False),
        sa.Column('update_ts', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_calendar_subscription_user_id'), 'user_calendar_subscription', ['user_id'], unique=False)


def downgrade():
    # Drop indices and tables
    op.drop_index(op.f('ix_user_calendar_subscription_user_id'), table_name='user_calendar_subscription')
    op.drop_table('user_calendar_subscription')
    op.drop_index(op.f('ix_user_event_attendance_user_id'), table_name='user_event_attendance')
    op.drop_table('user_event_attendance')
    
    # Remove columns from event table
    op.drop_index(op.f('ix_event_creator_user_id'), table_name='event')
    op.drop_column('event', 'is_personal')
    op.drop_column('event', 'creator_user_id')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS subscriptiontype')
    op.execute('DROP TYPE IF EXISTS attendancestatus')