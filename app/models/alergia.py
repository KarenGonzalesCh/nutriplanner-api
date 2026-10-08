
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship 

from app.db.base import Base


class Alergia(Base):
    """Representa una alergia del catálogo de NutriPlanner."""

    __tablename__ = "alergia"

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
        secondary="alergia_ingrediente",
        back_populates="alergias"
    )

    
    perfiles_alimentarios: Mapped[list["PerfilAlimentario"]] = relationship(
        "PerfilAlimentario",
        secondary="perfil_alergia",
        back_populates="alergias"
    )



