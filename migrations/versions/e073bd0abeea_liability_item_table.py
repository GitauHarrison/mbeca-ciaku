"""liability item table

Revision ID: e073bd0abeea
Revises: d04fbec1f966
Create Date: 2022-06-15 14:46:17.076511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e073bd0abeea'
down_revision = 'd04fbec1f966'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('liability_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_liability_item_name'), 'liability_item', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_liability_item_name'), table_name='liability_item')
    op.drop_table('liability_item')
    # ### end Alembic commands ###
