
from sqlalchemy.orm import Session

from app.models.ingrediente import Ingrediente
from app.repositories.ingrediente import IngredienteRepository


class IngredienteService:

    def __init__(self, db: Session):
        self.repository = IngredienteRepository(db)

    def listar(self) -> list[Ingrediente]:
        return self.repository.listar()
