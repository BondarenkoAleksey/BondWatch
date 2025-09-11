"""add coupon_schedule table

Revision ID: ad970dfbb907
Revises: 7a6013e07ee6
Create Date: 2025-09-11 20:29:42.307075
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ad970dfbb907'
down_revision = '7a6013e07ee6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema: create coupon_schedule table."""
    op.create_table(
        'coupon_schedule',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('bond_id', sa.Integer, sa.ForeignKey('bonds.id', ondelete='CASCADE'), nullable=False),
        sa.Column('value', sa.Float, nullable=True),
        sa.Column('valueprc', sa.Float, nullable=True)
    )
    op.create_index(op.f('ix_coupon_schedule_bond_id'), 'coupon_schedule', ['bond_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema: drop coupon_schedule table."""
    op.drop_index(op.f('ix_coupon_schedule_bond_id'), table_name='coupon_schedule')
    op.drop_table('coupon_schedule')
