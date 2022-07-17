"""support table

Revision ID: 07a73f54cecc
Revises: 7895e274bbc0
Create Date: 2022-07-17 11:23:00.160886

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07a73f54cecc'
down_revision = '7895e274bbc0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('support',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('verification_phone', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('support', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_support_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_support_username'), ['username'], unique=True)

    with op.batch_alter_table('help', schema=None) as batch_op:
        batch_op.add_column(sa.Column('suppport_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'support', ['suppport_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('help', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('suppport_id')

    with op.batch_alter_table('support', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_support_username'))
        batch_op.drop_index(batch_op.f('ix_support_email'))

    op.drop_table('support')
    # ### end Alembic commands ###
