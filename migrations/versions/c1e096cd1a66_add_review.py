from alembic import op
import sqlalchemy as sa


revision = 'c1e096cd1a66'
down_revision = 'e111af54f4bb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('comment_event', sa.Column('approve_status', sa.Enum('APPROVED', 'DECLINED', name='approvestatuses', native_enum=False), nullable=True))
    op.add_column('comment_lecturer', sa.Column('approve_status', sa.Enum('APPROVED', 'DECLINED', name='approvestatuses', native_enum=False), nullable=True))
    op.add_column('photo', sa.Column('approve_status', sa.Enum('APPROVED', 'DECLINED', name='approvestatuses', native_enum=False), nullable=True))


def downgrade():
    op.drop_column('photo', 'approve_status')
    op.drop_column('comment_lecturer', 'approve_status')
    op.drop_column('comment_event', 'approve_status')
