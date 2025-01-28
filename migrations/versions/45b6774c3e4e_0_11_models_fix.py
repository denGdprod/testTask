"""0.11 models fix

Revision ID: 45b6774c3e4e
Revises: 4f9e0a142095
Create Date: 2025-01-27 03:47:59.525708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45b6774c3e4e'
down_revision = '4f9e0a142095'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('partner', schema=None) as batch_op:
        batch_op.drop_index('ix_partner_telegram_id')
        batch_op.drop_column('telegram_id')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('telegram_id', sa.Integer(), nullable=False))
        batch_op.create_index(batch_op.f('ix_user_telegram_id'), ['telegram_id'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_telegram_id'))
        batch_op.drop_column('telegram_id')

    with op.batch_alter_table('partner', schema=None) as batch_op:
        batch_op.add_column(sa.Column('telegram_id', sa.INTEGER(), nullable=False))
        batch_op.create_index('ix_partner_telegram_id', ['telegram_id'], unique=1)

    # ### end Alembic commands ###
