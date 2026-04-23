"""Many to Many events to groups

Revision ID: 55a049fde8f4
Revises: fe04c8baa5ab
Create Date: 2023-07-02 22:58:17.045433

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '55a049fde8f4'
down_revision = 'fe04c8baa5ab'
branch_labels = None
depends_on = None

e = op.get_bind()


def merge_groups(res):
    to_delete = []
    pairs = []
    for old_ids, group_ids in res:
        save = old_ids.pop()
        to_delete.extend(old_ids)
        pairs.extend([(save, x) for x in group_ids])
    return to_delete, pairs


def upgrade():
    op.create_table(
        'events_groups',
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['event_id'],
            ['event.id'],
        ),
        sa.ForeignKeyConstraint(
            ['group_id'],
            ['group.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    res = e.execute(
        sa.text(
            """
        with inner_q as (
            select 
                name, 
                start_ts, 
                end_ts, 
                array_agg(id) as old_ids, 
                array_agg(group_id) as group_ids, 
                count(*) as groups_incl
            from "event" e 
            where not is_deleted
            group by name, start_ts, end_ts
        )
        select old_ids, group_ids
        from inner_q
    """
        )
    ).all()

    to_delete, pairs = merge_groups(res)
    delete_old_events_query = (
        f"""UPDATE event SET is_deleted = True WHERE id IN ({', '.join([str(x) for x in to_delete])})"""
    )
    list_ = '), ('.join([str(x) + ', ' + str(y) for x, y in pairs])
    if not list_:
        return
    create_new_links_query = f"""INSERT INTO events_groups(event_id, group_id) VALUES ({list_})"""
    e.execute(sa.text(delete_old_events_query))
    e.execute(sa.text(create_new_links_query))
    op.drop_constraint('lesson_group_id_fkey', 'event', type_='foreignkey')
    op.drop_column('event', 'group_id')


def downgrade():
    op.add_column('event', sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('lesson_group_id_fkey', 'event', 'group', ['group_id'], ['id'])
    op.drop_table('events_groups')
