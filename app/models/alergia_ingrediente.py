
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AlergiaIngrediente(Base):
    """Relaciona las alergias con los ingredientes restringidos."""

    __tablename__ = "alergia_ingrediente"

    alergia_id: Mapped[int] = mapped_column(
        ForeignKey("alergia.id"),
        primary_key=True
    )

    ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey("ingrediente.id"),
        primary_key=True
    )
