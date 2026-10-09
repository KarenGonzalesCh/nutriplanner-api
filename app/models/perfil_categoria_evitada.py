
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PerfilCategoriaEvitada(Base):
    """Relaciona perfiles alimentarios con categorías de alimentos evitadas."""

    __tablename__ = "perfil_categoria_evitada"

    perfil_id: Mapped[int] = mapped_column(
        ForeignKey("perfil_alimentario.id"),
        primary_key=True
    )

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categoria_alimento.id"),
        primary_key=True
    )
