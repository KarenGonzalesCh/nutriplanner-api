"""unificar migraciones generador y preferencias

Revision ID: 1a77b668d21f
Revises: 1d7690bacee8, 63437b190377
Create Date: 2026-10-31 01:11:34.067159

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a77b668d21f'
down_revision: Union[str, Sequence[str], None] = ('1d7690bacee8', '63437b190377')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
