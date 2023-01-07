"""create users table

Revision ID: debc3c807ff6
Revises: 
Create Date: 2023-01-06 14:02:06.419764

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'debc3c807ff6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users', 
    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
    sa.Column('username', sa.String(30), unique=True, nullable=False),
    sa.Column('email', sa.String(30), unique=True, nullable=False))
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
