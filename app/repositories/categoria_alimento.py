
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categoria_alimento import CategoriaAlimento


class CategoriaAlimentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[CategoriaAlimento]:
        consulta = select(CategoriaAlimento).order_by(
            CategoriaAlimento.nombre
        )

        return list(self.db.scalars(consulta).all())
