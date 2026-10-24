
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente


class RecetaRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Receta]:
        consulta = (
            select(Receta)
            .where(Receta.activa.is_(True))
            .options(
                selectinload(Receta.ingredientes)
                .selectinload(RecetaIngrediente.ingrediente),
                selectinload(Receta.tipos_comida),
            )
            .order_by(Receta.nombre)
        )

        return list(self.db.scalars(consulta).all())

    def obtener_por_id(self, receta_id: int) -> Receta | None:
        consulta = (
            select(Receta)
            .where(
                Receta.id == receta_id,
                Receta.activa.is_(True),
            )
            .options(
                selectinload(Receta.ingredientes)
                .selectinload(RecetaIngrediente.ingrediente),
                selectinload(Receta.tipos_comida),
            )
        )

        return self.db.scalar(consulta)
