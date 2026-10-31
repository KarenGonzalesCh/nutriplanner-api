
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CuentaRecetaFavorita(Base):
    """Relaciona una cuenta con una receta favorita."""

    __tablename__ = "cuenta_receta_favorita"

    cuenta_id: Mapped[int] = mapped_column(
        ForeignKey("cuenta.id", ondelete="CASCADE"),
        primary_key=True,
    )

    receta_id: Mapped[int] = mapped_column(
        ForeignKey("receta.id", ondelete="CASCADE"),
        primary_key=True,
    )
