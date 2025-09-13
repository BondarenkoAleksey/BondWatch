"""Add has_offer and offer_date fields to Bond with batch mode for SQLite

Revision ID: 39089a7f39e1
Revises: 7a42eafdbd79
Create Date: 2025-09-13 19:24:07.063791
"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '39089a7f39e1'
down_revision: Union[str, Sequence[str], None] = '7a42eafdbd79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем новые колонки к таблице bonds
    with op.batch_alter_table("bonds") as batch_op:
        batch_op.add_column(sa.Column("has_offer", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("offer_date", sa.Date(), nullable=True))

    # Добавляем уникальный constraint к таблице coupon_schedule
    with op.batch_alter_table("coupon_schedule") as batch_op:
        batch_op.create_unique_constraint(
            'uq_coupon_bond_date',
            ['bond_id', 'coupon_date']
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем constraint
    with op.batch_alter_table("coupon_schedule") as batch_op:
        batch_op.drop_constraint('uq_coupon_bond_date', type_='unique')

    # Удаляем новые колонки
    with op.batch_alter_table("bonds") as batch_op:
        batch_op.drop_column("offer_date")
        batch_op.drop_column("has_offer")
