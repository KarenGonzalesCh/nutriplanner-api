
"""Agregar campos para verificación de correo electrónico.

Revision ID: bd127c2c0a11
Revises: e333168a5e79
"""

from alembic import op
import sqlalchemy as sa


revision = "bd127c2c0a11"
down_revision = "e333168a5e79"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Agregar el estado de verificación.
    op.add_column(
        "cuenta",
        sa.Column(
            "correo_verificado",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    # 2. Mantener habilitadas las cuentas existentes.
    # No queremos bloquear a quienes ya usan NutriPlanner.
    op.execute(
        "UPDATE cuenta SET correo_verificado = TRUE"
    )

    # 3. Agregar los datos necesarios para verificar el email.
    op.add_column(
        "cuenta",
        sa.Column(
            "verificacion_token_hash",
            sa.String(64),
            nullable=True,
        ),
    )

    op.add_column(
        "cuenta",
        sa.Column(
            "verificacion_expira_en",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "cuenta",
        sa.Column(
            "verificacion_enviada_en",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # 4. El hash de cada token debe ser único.
    op.create_index(
        "ix_cuenta_verificacion_token_hash",
        "cuenta",
        ["verificacion_token_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cuenta_verificacion_token_hash",
        table_name="cuenta",
    )

    with op.batch_alter_table("cuenta") as batch_op:
        batch_op.drop_column("verificacion_enviada_en")
        batch_op.drop_column("verificacion_expira_en")
        batch_op.drop_column("verificacion_token_hash")
        batch_op.drop_column("correo_verificado")
