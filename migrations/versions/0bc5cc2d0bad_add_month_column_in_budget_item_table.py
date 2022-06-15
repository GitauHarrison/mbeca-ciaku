"""add month column in budget item table

Revision ID: 0bc5cc2d0bad
Revises: b8d7a8a0d1ad
Create Date: 2022-06-16 00:19:08.231947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bc5cc2d0bad'
down_revision = 'b8d7a8a0d1ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('budget_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('month', sa.String(length=64), nullable=True))
        batch_op.create_index(batch_op.f('ix_budget_item_month'), ['month'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('budget_item', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_budget_item_month'))
        batch_op.drop_column('month')

    # ### end Alembic commands ###
