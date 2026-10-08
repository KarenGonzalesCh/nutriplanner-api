
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PerfilAlergia(Base):
    """Relaciona los perfiles alimentarios con sus alergias."""

    __tablename__ = "perfil_alergia"

    perfil_id: Mapped[int] = mapped_column(
        ForeignKey("perfil_alimentario.id"),
        primary_key=True
    )

    alergia_id: Mapped[int] = mapped_column(
        ForeignKey("alergia.id"),
        primary_key=True
    )
