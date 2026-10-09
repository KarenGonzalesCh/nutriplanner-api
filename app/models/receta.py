
from sqlalchemy import Boolean, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import NivelDificultad
from app.db.base import Base


class Receta(Base):
    """Representa una receta del catálogo de NutriPlanner."""

    __tablename__ = "receta"

    id: Mapped[int] = mapped_column(primary_key=True)

    nombre: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    pasos: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    tiempo_preparacion: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    dificultad: Mapped[NivelDificultad] = mapped_column(
        SQLEnum(NivelDificultad),
        nullable=False
    )

    info_nutricional: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    activa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    
    tipos_comida: Mapped[list["RecetaTipoComida"]] = relationship(
        "RecetaTipoComida",
        back_populates="receta"
    )

    
    ingredientes: Mapped[list["RecetaIngrediente"]] = relationship(
        "RecetaIngrediente",
        back_populates="receta"
    )






