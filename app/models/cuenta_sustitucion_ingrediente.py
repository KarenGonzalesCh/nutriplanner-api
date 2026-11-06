
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CuentaSustitucionIngrediente(Base):
    """
    Guarda la alternativa seleccionada por un usuario
    para un ingrediente específico de una receta.
    """

    __tablename__ = "cuenta_sustitucion_ingrediente"

    cuenta_id: Mapped[int] = mapped_column(
        ForeignKey("cuenta.id", ondelete="CASCADE"),
        primary_key=True,
    )

    receta_ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey("receta_ingrediente.id", ondelete="CASCADE"),
        primary_key=True,
    )

    alternativa_ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey("alternativa_ingrediente.id"),
        nullable=False,
    )
