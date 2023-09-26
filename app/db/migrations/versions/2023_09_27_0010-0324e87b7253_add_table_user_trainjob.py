"""Add table User, trainJob

Revision ID: 0324e87b7253
Revises: 
Create Date: 2023-09-27 00:10:10.519193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0324e87b7253'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_index(op.f('ix_user_user_id'), 'user', ['user_id'], unique=False)
    op.create_table('train_job',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('run_id', sa.Uuid(), nullable=False),
        sa.Column('job_status', sa.Enum('TO_SUBMIT', 'SUBMITTED', 'PEDDING', 'LAUNCHED', 'STARTING', 'RUNNING', 'SUCCEEDED', 'FAILED', name='trainjobstatus'), nullable=False),
        sa.Column('job_type', sa.Enum('CREATE', 'RESUME', name='trainjobtype'), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('train_node_id', sa.Uuid(), nullable=True),
        sa.Column('nn_model_config', sa.JSON(), nullable=False),
        sa.Column('env_config', sa.JSON(), nullable=False),
        sa.Column('agent_config', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_train_job_id'), 'train_job', ['id'], unique=False)
    op.create_index(op.f('ix_train_job_job_status'), 'train_job', ['job_status'], unique=False)
    op.create_index(op.f('ix_train_job_job_type'), 'train_job', ['job_type'], unique=False)
    op.create_index(op.f('ix_train_job_run_id'), 'train_job', ['run_id'], unique=False)
    op.create_index(op.f('ix_train_job_train_node_id'), 'train_job', ['train_node_id'], unique=False)



def downgrade() -> None:
    op.drop_index(op.f('ix_train_job_train_node_id'), table_name='train_job')
    op.drop_index(op.f('ix_train_job_run_id'), table_name='train_job')
    op.drop_index(op.f('ix_train_job_job_type'), table_name='train_job')
    op.drop_index(op.f('ix_train_job_job_status'), table_name='train_job')
    op.drop_index(op.f('ix_train_job_id'), table_name='train_job')
    op.drop_table('train_job')
    op.drop_index(op.f('ix_user_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_table('user')
