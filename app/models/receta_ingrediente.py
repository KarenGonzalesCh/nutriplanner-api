
from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RecetaIngrediente(Base):
    """Representa un ingrediente y su cantidad dentro de una receta."""

    __tablename__ = "receta_ingrediente"

    __table_args__ = (
        UniqueConstraint(
            "receta_id",
            "ingrediente_id",
            name="uq_receta_ingrediente"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    receta_id: Mapped[int] = mapped_column(
        ForeignKey("receta.id"),
        nullable=False
    )

    ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey("ingrediente.id"),
        nullable=False
    )

    cantidad: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    unidad: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    
    receta: Mapped["Receta"] = relationship(
        "Receta",
        back_populates="ingredientes"
    )

    
    ingrediente: Mapped["Ingrediente"] = relationship(
        "Ingrediente",
        back_populates="recetas_ingrediente"
    )


