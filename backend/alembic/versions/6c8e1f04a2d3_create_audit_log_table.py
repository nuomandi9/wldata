"""create audit_log table

Revision ID: 6c8e1f04a2d3
Revises: 5b7a3d92e10c
Create Date: 2026-05-21 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '6c8e1f04a2d3'
down_revision: Union[str, None] = '5b7a3d92e10c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sys_audit_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=True),
        sa.Column('target_id', sa.String(length=64), nullable=True),
        sa.Column('detail', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('ip', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['sys_user.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sys_audit_log_action', 'sys_audit_log', ['action'])
    op.create_index('ix_sys_audit_log_created_at', 'sys_audit_log', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_sys_audit_log_created_at', table_name='sys_audit_log')
    op.drop_index('ix_sys_audit_log_action', table_name='sys_audit_log')
    op.drop_table('sys_audit_log')
