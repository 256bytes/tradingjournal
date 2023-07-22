"""alter in Research table tgt_sl column default to open from live

Revision ID: 8af9098d77a2
Revises: 86a5df7c1c6b
Create Date: 2023-06-15 11:22:36.863424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8af9098d77a2'
down_revision = '86a5df7c1c6b'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    # Step 1: Add a new temporary column with the desired default value
    op.add_column('Research', sa.Column('tgt_sl_temp', sa.String(), server_default='open'))

    # Step 2: Copy the data from the original column to the temporary column
    op.execute('UPDATE Research SET tgt_sl_temp = tgt_sl')

    # Step 3: Drop the original column
    op.drop_column('Research', 'tgt_sl')

    # Step 4: Rename the temporary column to the original column
    op.alter_column('Research', 'tgt_sl_temp', new_column_name='tgt_sl')

def downgrade():
    # Step 1: Add a new temporary column with the desired default value
    op.add_column('Research', sa.Column('tgt_sl_temp', sa.String(), server_default='open'))

    # Step 2: Copy the data from the temporary column to the original column
    op.execute('UPDATE Research SET tgt_sl = tgt_sl_temp')

    # Step 3: Drop the temporary column
    op.drop_column('Research', 'tgt_sl_temp')

    # Step 4: Alter the original column to add back the default value
    op.alter_column('Research', 'tgt_sl', server_default="live")



