"""Add table player data

Revision ID: 3c4c8517b952
Revises: 0324e87b7253
Create Date: 2023-10-13 18:20:27.305773

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c4c8517b952'
down_revision: Union[str, None] = '0324e87b7253'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('pubkey', sa.String(), nullable=False))
    op.add_column('user', sa.Column('username', sa.String(), nullable=False))
    op.add_column('user', sa.Column('bio', sa.String(), nullable=True))
    op.add_column('user', sa.Column('image_url', sa.String(), nullable=True))
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=False))
    op.add_column('user', sa.Column('player_data', sa.JSON(), nullable=True))
    op.create_index(op.f('ix_user_bio'), 'user', ['bio'], unique=False)
    op.create_index(op.f('ix_user_image_url'), 'user', ['image_url'], unique=False)
    op.create_index(op.f('ix_user_pubkey'), 'user', ['pubkey'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_pubkey'), table_name='user')
    op.drop_index(op.f('ix_user_image_url'), table_name='user')
    op.drop_index(op.f('ix_user_bio'), table_name='user')
    op.drop_column('user', 'player_data')
    op.drop_column('user', 'is_admin')
    op.drop_column('user', 'image_url')
    op.drop_column('user', 'bio')
    op.drop_column('user', 'username')
    op.drop_column('user', 'pubkey')
