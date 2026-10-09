
from sqlalchemy import Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TipoComida
from app.db.base import Base


class RecetaTipoComida(Base):
    """Relaciona una receta con sus tipos de comida."""

    __tablename__ = "receta_tipo_comida"

    receta_id: Mapped[int] = mapped_column(
        ForeignKey("receta.id"),
        primary_key=True
    )

    tipo_comida: Mapped[TipoComida] = mapped_column(
        SQLEnum(TipoComida),
        primary_key=True
    )

    
    receta: Mapped["Receta"] = relationship(
        "Receta",
        back_populates="tipos_comida"
    )

