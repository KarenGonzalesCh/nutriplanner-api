
from sqlalchemy import ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import NivelDificultad
from app.db.base import Base


class PerfilAlimentario(Base):
    """Almacena la configuración alimentaria de un usuario."""

    __tablename__ = "perfil_alimentario"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    cuenta_id: Mapped[int] = mapped_column(
        ForeignKey("cuenta.id"),
        unique=True,
        nullable=False
    )

    nivel_culinario: Mapped[NivelDificultad] = mapped_column(
        SQLEnum(NivelDificultad),
        nullable=False,
        default=NivelDificultad.PRINCIPIANTE
    )

    cuenta = relationship("Cuenta", back_populates="perfil_alimentario")

    
    alergias: Mapped[list["Alergia"]] = relationship(
        "Alergia",
        secondary="perfil_alergia",
        back_populates="perfiles_alimentarios"
    )

