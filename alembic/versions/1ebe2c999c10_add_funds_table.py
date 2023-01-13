"""add funds table

Revision ID: 1ebe2c999c10
Revises: 99453ee93e88
Create Date: 2023-01-12 15:54:58.368857

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1ebe2c999c10'
down_revision = '99453ee93e88'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('funds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('trading_code', sa.String(length=45), nullable=False),
    sa.Column('pay_in', sa.Integer(), nullable=False),
    sa.Column('pay_out', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('test')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('account', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('script', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('total_qty', mysql.VARCHAR(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('funds')
    # ### end Alembic commands ###
