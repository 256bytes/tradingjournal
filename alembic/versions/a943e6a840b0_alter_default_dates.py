"""alter default dates

Revision ID: a943e6a840b0
Revises: 18a21eafeedd
Create Date: 2023-01-12 16:28:02.635714

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a943e6a840b0'
down_revision = '18a21eafeedd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('funds', 'date',
               existing_type=mysql.DATETIME(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('funds', 'date',
               existing_type=mysql.DATETIME(),
               nullable=True)
    # ### end Alembic commands ###