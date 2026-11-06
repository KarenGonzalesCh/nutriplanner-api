
"""Crear tabla de sustituciones seleccionadas por usuario.

Revision ID: a2f8dea87e33
Revises: 2d481a823123
"""

from alembic import op
import sqlalchemy as sa


revision = "a2f8dea87e33"
down_revision = "2d481a823123"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crear la tabla para guardar sustituciones por usuario."""

    op.create_table(
        "cuenta_sustitucion_ingrediente",

        sa.Column(
            "cuenta_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "receta_ingrediente_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "alternativa_ingrediente_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["cuenta_id"],
            ["cuenta.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["receta_ingrediente_id"],
            ["receta_ingrediente.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["alternativa_ingrediente_id"],
            ["alternativa_ingrediente.id"],
        ),

        sa.PrimaryKeyConstraint(
            "cuenta_id",
            "receta_ingrediente_id",
        ),
    )


def downgrade() -> None:
    """Eliminar la tabla si se revierte la migración."""

    op.drop_table("cuenta_sustitucion_ingrediente")
