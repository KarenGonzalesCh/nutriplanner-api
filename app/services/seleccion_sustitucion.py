
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alternativa_ingrediente import AlternativaIngrediente
from app.models.cuenta_sustitucion_ingrediente import (
    CuentaSustitucionIngrediente,
)
from app.models.receta_ingrediente import RecetaIngrediente

from app.repositories.receta import RecetaRepository
from app.repositories.perfil_alimentario import (
    PerfilAlimentarioRepository,
)

from app.schemas.seleccion_sustitucion import (
    SustitucionGuardadaResponse,
)

from app.services.compatibilidad_ingrediente import (
    es_ingrediente_compatible,
)


class RecetaNoDisponibleError(Exception):
    pass


class IngredienteNoEncontradoError(Exception):
    pass


class PerfilNoConfiguradoError(Exception):
    pass


class AlternativaNoValidaError(Exception):
    pass


class SeleccionSustitucionService:

    def __init__(self, db: Session):
        self.db = db
        self.recetas = RecetaRepository(db)
        self.perfiles = PerfilAlimentarioRepository(db)

    def _obtener_receta(self, receta_id: int):
        receta = self.recetas.obtener_por_id(receta_id)

        if receta is None:
            raise RecetaNoDisponibleError(
                "La receta no existe o no está disponible"
            )

        return receta

    def _obtener_posicion(
        self,
        receta_id: int,
        receta_ingrediente_id: int,
    ):
        receta = self._obtener_receta(receta_id)

        for posicion in receta.ingredientes:
            if posicion.id == receta_ingrediente_id:
                return posicion

        raise IngredienteNoEncontradoError(
            "El ingrediente no pertenece a esta receta"
        )

    def _obtener_perfil(self, cuenta_id: int):
        perfil = self.perfiles.obtener_por_cuenta(cuenta_id)

        if perfil is None:
            raise PerfilNoConfiguradoError(
                "Debés configurar tu perfil alimentario primero"
            )

        return perfil

    @staticmethod
    def _preparar_respuesta(
        receta_id: int,
        alternativa: AlternativaIngrediente,
    ) -> SustitucionGuardadaResponse:

        ingrediente = alternativa.ingrediente_alternativo

        return SustitucionGuardadaResponse(
            receta_id=receta_id,
            receta_ingrediente_id=alternativa.receta_ingrediente_id,
            alternativa_id=alternativa.id,
            ingrediente_alternativo_id=ingrediente.id,
            nombre=ingrediente.nombre,
            cantidad=alternativa.cantidad,
            unidad=alternativa.unidad,
        )

    def guardar(
        self,
        cuenta_id: int,
        receta_id: int,
        receta_ingrediente_id: int,
        alternativa_id: int,
    ) -> SustitucionGuardadaResponse:

        posicion = self._obtener_posicion(
            receta_id,
            receta_ingrediente_id,
        )

        perfil = self._obtener_perfil(cuenta_id)

        # Solo se sustituyen ingredientes restringidos.
        if es_ingrediente_compatible(
            posicion.ingrediente,
            perfil,
        ):
            raise AlternativaNoValidaError(
                "Este ingrediente no requiere sustitución"
            )

        # La alternativa debe pertenecer al ingrediente
        # concreto de esta receta.
        alternativa = next(
            (
                item
                for item in posicion.alternativas
                if item.id == alternativa_id
            ),
            None,
        )

        if alternativa is None:
            raise AlternativaNoValidaError(
                "La alternativa no corresponde a este ingrediente"
            )

        # Verificar alergias, ingredientes y categorías evitadas.
        if not es_ingrediente_compatible(
            alternativa.ingrediente_alternativo,
            perfil,
        ):
            raise AlternativaNoValidaError(
                "La alternativa no es compatible con tu perfil"
            )

        registro = self.db.get(
            CuentaSustitucionIngrediente,
            (cuenta_id, receta_ingrediente_id),
        )

        if registro is None:
            registro = CuentaSustitucionIngrediente(
                cuenta_id=cuenta_id,
                receta_ingrediente_id=receta_ingrediente_id,
                alternativa_ingrediente_id=alternativa.id,
            )
            self.db.add(registro)
        else:
            # Si ya había una elección, reemplazarla.
            registro.alternativa_ingrediente_id = alternativa.id

        self.db.commit()

        return self._preparar_respuesta(
            receta_id,
            alternativa,
        )

    def listar(
        self,
        cuenta_id: int,
        receta_id: int,
    ) -> list[SustitucionGuardadaResponse]:

        receta = self._obtener_receta(receta_id)
        perfil = self._obtener_perfil(cuenta_id)

        posiciones = {
            posicion.id: posicion
            for posicion in receta.ingredientes
        }

        consulta = (
            select(CuentaSustitucionIngrediente)
            .join(
                RecetaIngrediente,
                RecetaIngrediente.id
                == CuentaSustitucionIngrediente.receta_ingrediente_id,
            )
            .where(
                CuentaSustitucionIngrediente.cuenta_id == cuenta_id,
                RecetaIngrediente.receta_id == receta_id,
            )
        )

        registros = self.db.scalars(consulta).all()
        resultado = []

        for registro in registros:
            posicion = posiciones.get(
                registro.receta_ingrediente_id
            )

            if posicion is None:
                continue

            alternativa = next(
                (
                    item
                    for item in posicion.alternativas
                    if item.id == registro.alternativa_ingrediente_id
                ),
                None,
            )

            if alternativa is None:
                continue

            # No mostrar como válida una elección que dejó
            # de ser compatible tras modificar el perfil.
            if es_ingrediente_compatible(
                posicion.ingrediente,
                perfil,
            ):
                continue

            if not es_ingrediente_compatible(
                alternativa.ingrediente_alternativo,
                perfil,
            ):
                continue

            resultado.append(
                self._preparar_respuesta(
                    receta_id,
                    alternativa,
                )
            )

        return resultado

    def eliminar(
        self,
        cuenta_id: int,
        receta_id: int,
        receta_ingrediente_id: int,
    ) -> bool:

        self._obtener_posicion(
            receta_id,
            receta_ingrediente_id,
        )

        registro = self.db.get(
            CuentaSustitucionIngrediente,
            (cuenta_id, receta_ingrediente_id),
        )

        if registro is None:
            return False

        self.db.delete(registro)
        self.db.commit()

        return True
