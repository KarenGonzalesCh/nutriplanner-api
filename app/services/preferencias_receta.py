
from sqlalchemy.orm import Session

from app.models.receta import Receta
from app.repositories.preferencias_receta import (
    PreferenciasRecetaRepository,
)


class RecetaNoExisteError(Exception):
    pass


class PreferenciasRecetaService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = PreferenciasRecetaRepository(db)

    def _verificar_receta(self, receta_id: int) -> None:
        receta = self.db.get(Receta, receta_id)

        if receta is None:
            raise RecetaNoExisteError("La receta no existe")

    # FAVORITAS

    def listar_favoritas(self, cuenta_id: int) -> list[int]:
        return self.repository.listar_favoritas(cuenta_id)

    def agregar_favorita(self, cuenta_id: int, receta_id: int) -> None:
        self._verificar_receta(receta_id)

        favoritas = self.repository.listar_favoritas(cuenta_id)

        if receta_id not in favoritas:
            self.repository.agregar_favorita(cuenta_id, receta_id)

    def quitar_favorita(self, cuenta_id: int, receta_id: int) -> bool:
        return self.repository.quitar_favorita(cuenta_id, receta_id)

    # EXCLUSIONES

    def listar_excluidas(self, cuenta_id: int) -> list[int]:
        return self.repository.listar_excluidas(cuenta_id)

    def agregar_exclusion(self, cuenta_id: int, receta_id: int) -> None:
        self._verificar_receta(receta_id)

        excluidas = self.repository.listar_excluidas(cuenta_id)

        if receta_id not in excluidas:
            self.repository.agregar_exclusion(cuenta_id, receta_id)

    def quitar_exclusion(self, cuenta_id: int, receta_id: int) -> bool:
        return self.repository.quitar_exclusion(cuenta_id, receta_id)
