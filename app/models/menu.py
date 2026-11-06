
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TipoComida
from app.db.base import Base


class Menu(Base):
    """Menú confirmado y guardado por una cuenta."""

    __tablename__ = "menu"

    __table_args__ = (
        CheckConstraint(
            "cantidad_dias BETWEEN 1 AND 7",
            name="ck_menu_cantidad_dias",
        ),
        CheckConstraint(
            "comensales > 0",
            name="ck_menu_comensales",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    cuenta_id: Mapped[int] = mapped_column(
        ForeignKey("cuenta.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    cantidad_dias: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    comensales: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    tamano_porcion: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="NORMAL",
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    comidas: Mapped[list["MenuComida"]] = relationship(
        "MenuComida",
        back_populates="menu",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class MenuComida(Base):
    """Comida individual con la receta conservada históricamente."""

    __tablename__ = "menu_comida"

    __table_args__ = (
        UniqueConstraint(
            "menu_id",
            "dia",
            "tipo_comida",
            name="uq_menu_comida_dia_tipo",
        ),
        CheckConstraint(
            "dia BETWEEN 1 AND 7",
            name="ck_menu_comida_dia",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    menu_id: Mapped[int] = mapped_column(
        ForeignKey("menu.id", ondelete="CASCADE"),
        nullable=False,
    )

    dia: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    tipo_comida: Mapped[TipoComida] = mapped_column(
        SQLEnum(TipoComida),
        nullable=False,
    )

    receta_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    instantanea: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    menu: Mapped["Menu"] = relationship(
        "Menu",
        back_populates="comidas",
    )

