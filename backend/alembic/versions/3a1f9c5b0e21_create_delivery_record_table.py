"""create delivery_record business table

Revision ID: 3a1f9c5b0e21
Revises: 69d2118e1afc
Create Date: 2026-05-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3a1f9c5b0e21'
down_revision: Union[str, None] = '69d2118e1afc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'biz_delivery_record',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('record_date', sa.Date(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('deliverer_id', sa.Integer(), nullable=True),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('customer_count', sa.Integer(), nullable=True),
        sa.Column('delivery_count', sa.Integer(), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('warn_notes', sa.Text(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('extra', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['vehicle_id'], ['dict_vehicle.id'], ),
        sa.ForeignKeyConstraint(['driver_id'], ['dict_person.id'], ),
        sa.ForeignKeyConstraint(['deliverer_id'], ['dict_person.id'], ),
        sa.ForeignKeyConstraint(['route_id'], ['dict_route.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['sys_user.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_biz_delivery_record_record_date',
        'biz_delivery_record',
        ['record_date'],
    )


def downgrade() -> None:
    op.drop_index('ix_biz_delivery_record_record_date', table_name='biz_delivery_record')
    op.drop_table('biz_delivery_record')
