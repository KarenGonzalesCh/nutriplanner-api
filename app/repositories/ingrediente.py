
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ingrediente import Ingrediente


class IngredienteRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Ingrediente]:
        consulta = select(Ingrediente).order_by(
            Ingrediente.nombre
        )

        return list(self.db.scalars(consulta).all())
