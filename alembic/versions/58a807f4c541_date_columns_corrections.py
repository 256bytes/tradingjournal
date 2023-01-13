"""date columns corrections

Revision ID: 58a807f4c541
Revises: a943e6a840b0
Create Date: 2023-01-12 16:42:16.825640

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '58a807f4c541'
down_revision = 'a943e6a840b0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'date',
               existing_type=mysql.DATETIME(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'date',
               existing_type=mysql.DATETIME(),
               nullable=True)
    # ### end Alembic commands ###
