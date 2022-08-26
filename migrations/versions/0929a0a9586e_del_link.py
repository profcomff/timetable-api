"""del_link

Revision ID: 0929a0a9586e
Revises: c66359fe2d1e
Create Date: 2022-08-26 22:06:12.799690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0929a0a9586e'
down_revision = 'c66359fe2d1e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('lecturer_avatar_link_fkey', 'lecturer', type_='foreignkey')
    op.drop_column('lecturer', 'avatar_link')


def downgrade():
    op.add_column('lecturer', sa.Column('avatar_link', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_foreign_key('lecturer_avatar_link_fkey', 'lecturer', 'photo', ['avatar_link'], ['link'])
