"""remove unique constraint from data column

Revision ID: 27c14ea88775
Revises: bce656f142b2
Create Date: 2022-06-15 22:48:44.818301

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27c14ea88775'
down_revision = 'bce656f142b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('actual_income', schema=None) as batch_op:
        batch_op.drop_index('ix_actual_income_date')
        batch_op.create_index(batch_op.f('ix_actual_income_date'), ['date'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('actual_income', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_actual_income_date'))
        batch_op.create_index('ix_actual_income_date', ['date'], unique=False)

    # ### end Alembic commands ###