"""agregar porciones base a receta

Revision ID: 1d7690bacee8
Revises: 9daba92d0e39
Create Date: 2026-10-30 23:47:39.457803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d7690bacee8'
down_revision: Union[str, Sequence[str], None] = '9daba92d0e39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega porciones_base a la tabla receta."""
    op.add_column(
        "receta",
        sa.Column(
            "porciones_base",
            sa.Integer(),
            nullable=True,
        ),
    )

def downgrade() -> None:
    """Elimina porciones_base de la tabla receta."""
    op.drop_column("receta", "porciones_base")