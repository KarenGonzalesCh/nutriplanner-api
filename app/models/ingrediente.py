
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ingrediente(Base):
    """Representa un ingrediente del catálogo de NutriPlanner."""

    __tablename__ = "ingrediente"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categoria_alimento.id"),
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    categoria: Mapped["CategoriaAlimento"] = relationship(
        "CategoriaAlimento",
        back_populates="ingredientes"
    )

    
    alergias: Mapped[list["Alergia"]] = relationship(
        "Alergia",
        secondary="alergia_ingrediente",
        back_populates="ingredientes"
    )

    
    perfiles_que_lo_evitan: Mapped[list["PerfilAlimentario"]] = relationship(
        "PerfilAlimentario",
        secondary="perfil_ingrediente_evitado",
        back_populates="ingredientes_evitados"
    )

    
    recetas_ingrediente: Mapped[list["RecetaIngrediente"]] = relationship(
        "RecetaIngrediente",
        back_populates="ingrediente"
    )



