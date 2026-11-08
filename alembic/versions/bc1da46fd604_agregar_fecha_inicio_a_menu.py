"""agregar fecha inicio a menu

Revision ID: bc1da46fd604
Revises: bd127c2c0a11
Create Date: 2026-11-07 18:05:18.040319

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc1da46fd604'
down_revision: Union[str, Sequence[str], None] = 'bd127c2c0a11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "menu",
        sa.Column("fecha_inicio", sa.Date(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("menu", "fecha_inicio")
