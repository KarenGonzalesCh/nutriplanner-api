from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AlternativaIngrediente(Base):
    """Alternativa permitida para un ingrediente dentro de una receta."""

    __tablename__ = "alternativa_ingrediente"

    __table_args__ = (
        UniqueConstraint(
            "receta_ingrediente_id",
            "ingrediente_alternativo_id",
            name="uq_alternativa_receta_ingrediente"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    receta_ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey("receta_ingrediente.id"),
        nullable=False
    )

    ingrediente_alternativo_id: Mapped[int] = mapped_column(
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

    receta_ingrediente: Mapped["RecetaIngrediente"] = relationship(
        "RecetaIngrediente",
        back_populates="alternativas"
    )

    ingrediente_alternativo: Mapped["Ingrediente"] = relationship(
        "Ingrediente"
    )
