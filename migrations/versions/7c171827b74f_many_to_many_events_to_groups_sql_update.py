"""Many to Many events to groups SQL UPDATE

Revision ID: 7c171827b74f
Revises: 55a049fde8f4
Create Date: 2023-07-02 23:07:02.440547

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '7c171827b74f'
down_revision = '55a049fde8f4'
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
    create_new_links_query = f"""INSERT INTO events_groups(event_id, group_id) VALUES ({'), ('.join([str(x) + ', ' + str(y) for x, y in pairs])})"""
    e.execute(sa.text(delete_old_events_query))
    e.execute(sa.text(create_new_links_query))


def downgrade():
    pass
