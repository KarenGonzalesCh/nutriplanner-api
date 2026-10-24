
from sqlalchemy.orm import Session

from app.models.perfil_alimentario import PerfilAlimentario
from app.repositories.perfil_alimentario import PerfilAlimentarioRepository
from app.schemas.perfil_alimentario import (
    PerfilAlimentarioCreate,
)


class PerfilYaExisteError(Exception):
    pass


class PerfilNoEncontradoError(Exception):
    pass


class CatalogoInvalidoError(Exception):
    pass


class PerfilAlimentarioService:

    def __init__(self, db: Session):
        self.repository = PerfilAlimentarioRepository(db)

    def obtener(self, cuenta_id: int) -> PerfilAlimentario:
        perfil = self.repository.obtener_por_cuenta(cuenta_id)

        if perfil is None:
            raise PerfilNoEncontradoError(
                "La cuenta no tiene un perfil alimentario"
            )

        return perfil

    def _asignar_preferencias(
        self,
        perfil: PerfilAlimentario,
        datos: PerfilAlimentarioCreate,
    ) -> None:
        alergias = self.repository.obtener_alergias(datos.alergias_ids)
        ingredientes = self.repository.obtener_ingredientes(
            datos.ingredientes_evitados_ids
        )
        categorias = self.repository.obtener_categorias(
            datos.categorias_evitadas_ids
        )

        if {a.id for a in alergias} != set(datos.alergias_ids):
            raise CatalogoInvalidoError("Hay alergias inexistentes")

        if {i.id for i in ingredientes} != set(
            datos.ingredientes_evitados_ids
        ):
            raise CatalogoInvalidoError("Hay ingredientes inexistentes")

        if {c.id for c in categorias} != set(
            datos.categorias_evitadas_ids
        ):
            raise CatalogoInvalidoError("Hay categorías inexistentes")

        perfil.nivel_culinario = datos.nivel_culinario
        perfil.alergias = alergias
        perfil.ingredientes_evitados = ingredientes
        perfil.categorias_evitadas = categorias

    def crear(
        self,
        cuenta_id: int,
        datos: PerfilAlimentarioCreate,
    ) -> PerfilAlimentario:
        if self.repository.obtener_por_cuenta(cuenta_id):
            raise PerfilYaExisteError(
                "La cuenta ya tiene un perfil alimentario"
            )

        perfil = PerfilAlimentario(cuenta_id=cuenta_id)
        self._asignar_preferencias(perfil, datos)

        return self.repository.guardar(perfil)

    def actualizar(
        self,
        cuenta_id: int,
        datos: PerfilAlimentarioCreate,
    ) -> PerfilAlimentario:
        perfil = self.obtener(cuenta_id)
        self._asignar_preferencias(perfil, datos)

        return self.repository.guardar(perfil)
