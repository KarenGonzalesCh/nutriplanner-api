
from sqlalchemy.orm import Session

from app.models.alergia import Alergia
from app.repositories.alergia import AlergiaRepository


class AlergiaService:

    def __init__(self, db: Session):
        self.repository = AlergiaRepository(db)

    def listar(self) -> list[Alergia]:
        return self.repository.listar()
