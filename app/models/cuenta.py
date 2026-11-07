from datetime import datetime

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import Rol
from app.db.base import Base


class Cuenta(Base):
    """Representa una cuenta de usuario o moderador."""

    __tablename__ = "cuenta"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombre_usuario: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    correo: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Indica si el usuario confirmó su dirección de correo.
    correo_verificado: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    # Hash del token de confirmación enviado por correo.
    verificacion_token_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        unique=True
    )

    # Fecha y hora de vencimiento del token.
    verificacion_expira_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Fecha y hora del último envío de confirmación.
    verificacion_enviada_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    rol: Mapped[Rol] = mapped_column(
        SQLEnum(Rol),
        nullable=False,
        default=Rol.USUARIO
    )

    perfil_alimentario: Mapped["PerfilAlimentario | None"] = relationship(
        "PerfilAlimentario",
        back_populates="cuenta",
        uselist=False
    )
