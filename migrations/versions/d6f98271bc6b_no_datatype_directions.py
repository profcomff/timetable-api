"""No datatype Directions

Revision ID: d6f98271bc6b
Revises: 8bae03e22feb
Create Date: 2022-08-20 02:44:28.203133

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6f98271bc6b'
down_revision = '8bae03e22feb'
branch_labels = None
depends_on = None

directions_native = sa.Enum('North', 'South', name="Directions")
directions = sa.Enum('North', 'South', native_enum=False)


def upgrade():
    # FIXME: Не надо бы с прода удалять столбцы не скопировав данные
    op.drop_column("room", "direction")
    directions_native.drop(op.get_bind(), checkfirst=True)
    op.add_column("room", sa.Column('direction', directions, nullable=True))


def downgrade():
    op.drop_column("room", "direction")
    directions_native.create(op.get_bind(), checkfirst=True)
    op.add_column("room", sa.Column('direction', directions_native, nullable=True))
