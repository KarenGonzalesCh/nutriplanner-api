
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PerfilIngredienteEvitado(Base):
    """Relaciona perfiles alimentarios con ingredientes evitados."""

    __tablename__ = "perfil_ingrediente_evitado"

    perfil_id: Mapped[int] = mapped_column(
        ForeignKey("perfil_alimentario.id"),
        primary_key=True
    )

    ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey("ingrediente.id"),
        primary_key=True
    )
