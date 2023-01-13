"""add debit and credit columns to funds table

Revision ID: a3bda0dd2725
Revises: 7969e876719e
Create Date: 2023-01-12 21:42:11.807516

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3bda0dd2725'
down_revision = '7969e876719e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('funds', sa.Column('debits', sa.Float(), nullable=False))
    op.add_column('funds', sa.Column('credits', sa.Float(), nullable=False))
    op.add_column('funds', sa.Column('balance', sa.Float(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('funds', 'balance')
    op.drop_column('funds', 'credits')
    op.drop_column('funds', 'debits')
    # ### end Alembic commands ###