"""Fix photo paths

Revision ID: 63263ee9e08e
Revises: 6d57978a236e
Create Date: 2023-03-20 15:15:20.345969

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '63263ee9e08e'
down_revision = '6d57978a236e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE photo SET link=REGEXP_REPLACE(link, '.*/([^/]+)$', '\\1', 'i')")


def downgrade():
    pass
