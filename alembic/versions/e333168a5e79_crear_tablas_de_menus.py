
"""Crear tablas de menus.

Revision ID: e333168a5e79
Revises: a2f8dea87e33
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "e333168a5e79"
down_revision = "a2f8dea87e33"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Un menú pertenece a una cuenta.
    op.create_table(
        "menu",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cuenta_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("cantidad_dias", sa.Integer(), nullable=False),
        sa.Column("comensales", sa.Integer(), nullable=False),
        sa.Column("tamano_porcion", sa.String(20), nullable=False),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["cuenta_id"],
            ["cuenta.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "cantidad_dias BETWEEN 1 AND 7",
            name="ck_menu_cantidad_dias",
        ),
        sa.CheckConstraint(
            "comensales > 0",
            name="ck_menu_comensales",
        ),
    )

    op.create_index(
        "ix_menu_cuenta_id",
        "menu",
        ["cuenta_id"],
    )

    # Reutilizar el enum existente en PostgreSQL.
    tipos = ["DESAYUNO", "ALMUERZO", "MERIENDA", "CENA"]

    if op.get_bind().dialect.name == "postgresql":
        tipo_comida = postgresql.ENUM(
            *tipos,
            name="tipocomida",
            create_type=False,
        )
    else:
        tipo_comida = sa.Enum(
            *tipos,
            name="tipocomida",
        )

    # Cada comida guarda una instantánea histórica.
    op.create_table(
        "menu_comida",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("menu_id", sa.Integer(), nullable=False),
        sa.Column("dia", sa.Integer(), nullable=False),
        sa.Column("tipo_comida", tipo_comida, nullable=False),
        sa.Column("receta_id", sa.Integer(), nullable=False),
        sa.Column("instantanea", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["menu_id"],
            ["menu.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "menu_id",
            "dia",
            "tipo_comida",
            name="uq_menu_comida_dia_tipo",
        ),
        sa.CheckConstraint(
            "dia BETWEEN 1 AND 7",
            name="ck_menu_comida_dia",
        ),
    )


def downgrade() -> None:
    op.drop_table("menu_comida")
    op.drop_index("ix_menu_cuenta_id", table_name="menu")
    op.drop_table("menu")
