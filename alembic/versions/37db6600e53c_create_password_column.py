"""create password column

Revision ID: 37db6600e53c
Revises: debc3c807ff6
Create Date: 2023-01-06 14:13:33.154468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37db6600e53c'
down_revision = 'debc3c807ff6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('hash_password', sa.String(60), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('users', 'hash_password')
    pass
