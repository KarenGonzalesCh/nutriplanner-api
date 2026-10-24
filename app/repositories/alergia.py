
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alergia import Alergia


class AlergiaRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Alergia]:
        consulta = select(Alergia).order_by(Alergia.nombre)

        return list(self.db.scalars(consulta).all())
