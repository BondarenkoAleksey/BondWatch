"""add coupon_schedule table

Revision ID: 7a6013e07ee6
Revises: 13a88baab0d6
Create Date: 2025-09-11 19:54:00.166685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a6013e07ee6'
down_revision: Union[str, Sequence[str], None] = '13a88baab0d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "coupon_schedule",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("bond_isin", sa.String, sa.ForeignKey("bonds.isin"), nullable=False, index=True),
        sa.Column("coupon_date", sa.Date, nullable=False),
        sa.Column("coupon_value", sa.Float, nullable=False),
    )


def downgrade():
    op.drop_table("coupon_schedule")
