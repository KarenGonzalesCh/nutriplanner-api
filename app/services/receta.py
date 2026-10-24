
from sqlalchemy.orm import Session

from app.models.receta import Receta
from app.models.perfil_alimentario import PerfilAlimentario
from app.repositories.receta import RecetaRepository
from app.repositories.perfil_alimentario import PerfilAlimentarioRepository
from app.services.evaluador_restricciones import (
    crear_evaluador_restricciones,
)
from app.schemas.receta import (
    RecetaResponse,
    RecetaIngredienteResponse,
)


class RecetaNoEncontradaError(Exception):
    pass


class PerfilRequeridoError(Exception):
    pass


class RecetaService:

    def __init__(self, db: Session):
        self.repository = RecetaRepository(db)
        self.perfil_repository = PerfilAlimentarioRepository(db)
        self.evaluador = crear_evaluador_restricciones()

    def _obtener_perfil(self, cuenta_id: int) -> PerfilAlimentario:
        perfil = self.perfil_repository.obtener_por_cuenta(cuenta_id)

        if perfil is None:
            raise PerfilRequeridoError(
                "Debés configurar tu perfil alimentario primero"
            )

        return perfil

    def _preparar_respuesta(self, receta: Receta) -> RecetaResponse:
        return RecetaResponse(
            id=receta.id,
            nombre=receta.nombre,
            pasos=receta.pasos,
            tiempo_preparacion=receta.tiempo_preparacion,
            dificultad=receta.dificultad,
            info_nutricional=receta.info_nutricional,
            tipos_comida=[
                relacion.tipo_comida
                for relacion in receta.tipos_comida
            ],
            ingredientes=[
                RecetaIngredienteResponse(
                    ingrediente_id=relacion.ingrediente_id,
                    nombre=relacion.ingrediente.nombre,
                    cantidad=relacion.cantidad,
                    unidad=relacion.unidad,
                )
                for relacion in receta.ingredientes
            ],
        )

    def listar(self, cuenta_id: int) -> list[RecetaResponse]:
        perfil = self._obtener_perfil(cuenta_id)
        recetas = self.repository.listar()

        return [
            self._preparar_respuesta(receta)
            for receta in recetas
            if self.evaluador.es_compatible(receta, perfil)
        ]

    def obtener_por_id(
        self,
        cuenta_id: int,
        receta_id: int,
    ) -> RecetaResponse:
        perfil = self._obtener_perfil(cuenta_id)
        receta = self.repository.obtener_por_id(receta_id)

        if receta is None:
            raise RecetaNoEncontradaError(
                "La receta no existe o no está disponible"
            )

        if not self.evaluador.es_compatible(receta, perfil):
            raise RecetaNoEncontradaError(
                "La receta no está disponible para tu perfil"
            )

        return self._preparar_respuesta(receta)
