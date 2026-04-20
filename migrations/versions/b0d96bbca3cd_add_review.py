import sqlalchemy as sa
from alembic import op


revision = 'b0d96bbca3cd'
down_revision = 'e111af54f4bb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'comment_event',
        sa.Column(
            'approve_status',
            sa.Enum('APPROVED', 'DECLINED', 'PENDING', name='approvestatuses', native_enum=False),
            nullable=False,
        ),
    )
    op.add_column(
        'comment_lecturer',
        sa.Column(
            'approve_status',
            sa.Enum('APPROVED', 'DECLINED', 'PENDING', name='approvestatuses', native_enum=False),
            nullable=False,
        ),
    )
    op.add_column(
        'photo',
        sa.Column(
            'approve_status',
            sa.Enum('APPROVED', 'DECLINED', 'PENDING', name='approvestatuses', native_enum=False),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column('photo', 'approve_status')
    op.drop_column('comment_lecturer', 'approve_status')
    op.drop_column('comment_event', 'approve_status')
