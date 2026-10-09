
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CategoriaAlimento(Base):
    """Representa una categoría de alimentos del catálogo."""

    __tablename__ = "categoria_alimento"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    ingredientes: Mapped[list["Ingrediente"]] = relationship(
        "Ingrediente",
        back_populates="categoria"
    )

    perfiles_que_la_evitan: Mapped[list["PerfilAlimentario"]] = relationship(
        "PerfilAlimentario",
        secondary="perfil_categoria_evitada",
        back_populates="categorias_evitadas"
    )
