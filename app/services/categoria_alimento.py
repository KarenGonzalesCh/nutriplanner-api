
from sqlalchemy.orm import Session

from app.models.categoria_alimento import CategoriaAlimento
from app.repositories.categoria_alimento import CategoriaAlimentoRepository


class CategoriaAlimentoService:

    def __init__(self, db: Session):
        self.repository = CategoriaAlimentoRepository(db)

    def listar(self) -> list[CategoriaAlimento]:
        return self.repository.listar()
