"""create all tables

Revision ID: bce656f142b2
Revises: 
Create Date: 2022-06-15 22:40:52.678516

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bce656f142b2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('actual_income',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('month', sa.String(length=64), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('date', sa.String(length=64), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('actual_income', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_actual_income_amount'), ['amount'], unique=False)
        batch_op.create_index(batch_op.f('ix_actual_income_date'), ['date'], unique=True)
        batch_op.create_index(batch_op.f('ix_actual_income_description'), ['description'], unique=False)
        batch_op.create_index(batch_op.f('ix_actual_income_month'), ['month'], unique=False)
        batch_op.create_index(batch_op.f('ix_actual_income_year'), ['year'], unique=False)

    op.create_table('asset_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('asset_item', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_asset_item_name'), ['name'], unique=True)

    op.create_table('budget_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('budget_item', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_budget_item_name'), ['name'], unique=True)

    op.create_table('income_source',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('income_source', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_income_source_name'), ['name'], unique=True)

    op.create_table('liability_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('liability_item', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_liability_item_name'), ['name'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('liability_item', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_liability_item_name'))

    op.drop_table('liability_item')
    with op.batch_alter_table('income_source', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_income_source_name'))

    op.drop_table('income_source')
    with op.batch_alter_table('budget_item', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_budget_item_name'))

    op.drop_table('budget_item')
    with op.batch_alter_table('asset_item', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_asset_item_name'))

    op.drop_table('asset_item')
    with op.batch_alter_table('actual_income', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_actual_income_year'))
        batch_op.drop_index(batch_op.f('ix_actual_income_month'))
        batch_op.drop_index(batch_op.f('ix_actual_income_description'))
        batch_op.drop_index(batch_op.f('ix_actual_income_date'))
        batch_op.drop_index(batch_op.f('ix_actual_income_amount'))

    op.drop_table('actual_income')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    # ### end Alembic commands ###
