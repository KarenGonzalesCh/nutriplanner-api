
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cuenta_receta_favorita import CuentaRecetaFavorita
from app.models.cuenta_receta_excluida import CuentaRecetaExcluida


class PreferenciasRecetaRepository:

    def __init__(self, db: Session):
        self.db = db

    # FAVORITAS

    def listar_favoritas(self, cuenta_id: int) -> list[int]:
        consulta = select(CuentaRecetaFavorita.receta_id).where(
            CuentaRecetaFavorita.cuenta_id == cuenta_id
        )

        return list(self.db.scalars(consulta).all())

    def agregar_favorita(self, cuenta_id: int, receta_id: int) -> None:
        favorita = CuentaRecetaFavorita(
            cuenta_id=cuenta_id,
            receta_id=receta_id,
        )

        self.db.add(favorita)
        self.db.commit()

    def quitar_favorita(self, cuenta_id: int, receta_id: int) -> bool:
        favorita = self.db.get(
            CuentaRecetaFavorita,
            (cuenta_id, receta_id),
        )

        if favorita is None:
            return False

        self.db.delete(favorita)
        self.db.commit()
        return True

    # EXCLUSIONES

    def listar_excluidas(self, cuenta_id: int) -> list[int]:
        consulta = select(CuentaRecetaExcluida.receta_id).where(
            CuentaRecetaExcluida.cuenta_id == cuenta_id
        )

        return list(self.db.scalars(consulta).all())

    def agregar_exclusion(self, cuenta_id: int, receta_id: int) -> None:
        exclusion = CuentaRecetaExcluida(
            cuenta_id=cuenta_id,
            receta_id=receta_id,
        )

        self.db.add(exclusion)
        self.db.commit()

    def quitar_exclusion(self, cuenta_id: int, receta_id: int) -> bool:
        exclusion = self.db.get(
            CuentaRecetaExcluida,
            (cuenta_id, receta_id),
        )

        if exclusion is None:
            return False

        self.db.delete(exclusion)
        self.db.commit()
        return True
