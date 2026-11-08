
from sqlalchemy.orm import Session

from app.models.menu import Menu, MenuComida
from app.repositories.perfil_alimentario import (
    PerfilAlimentarioRepository,
)
from app.repositories.receta import RecetaRepository
from app.schemas.menu import GuardarMenuRequest
from app.services.preferencias_receta import (
    PreferenciasRecetaService,
)
from app.services.validacion_menu import (
    ComidaMenuInvalidaError,
    construir_instantanea_comida,
)


class MenuInvalidoError(ValueError):
    """El menú no cumple las condiciones de guardado."""


class GuardarMenuService:
    """Valida y persiste menús confirmados por el usuario."""

    def __init__(self, db: Session):
        self.db = db
        self.recetas = RecetaRepository(db)
        self.perfiles = PerfilAlimentarioRepository(db)
        self.preferencias = PreferenciasRecetaService(db)

    def guardar(
        self,
        cuenta_id: int,
        datos: GuardarMenuRequest,
    ) -> Menu:

        # Obtener el perfil alimentario vigente.
        perfil = self.perfiles.obtener_por_cuenta(cuenta_id)

        if perfil is None:
            raise MenuInvalidoError(
                "Debés configurar tu perfil alimentario"
            )

        # Recuperar las exclusiones personales del usuario.
        recetas_excluidas = set(
            self.preferencias.listar_excluidas(cuenta_id)
        )

        # Validar que exista al menos una comida por día.
        dias_presentes = {
            comida.dia for comida in datos.comidas
        }

        dias_esperados = set(
            range(1, datos.cantidad_dias + 1)
        )

        if dias_presentes != dias_esperados:
            raise MenuInvalidoError(
                "El menú debe incluir comidas "
                "en todos los días configurados"
            )

        comidas_validadas = []

        # Validar todas las comidas antes de guardar.
        for comida in datos.comidas:

            receta = self.recetas.obtener_por_id(
                comida.receta_id
            )

            if receta is None:
                raise MenuInvalidoError(
                    f"La receta {comida.receta_id} "
                    "no existe o está desactivada"
                )

            # Una receta excluida requiere confirmación.
            if (
                receta.id in recetas_excluidas
                and not comida.confirma_receta_excluida
            ):
                raise MenuInvalidoError(
                    f"La receta {receta.nombre} está excluida. "
                    "Debés confirmar su selección manual."
                )

            # Verificar cada ingrediente y sustitución.
            try:
                instantanea = construir_instantanea_comida(
                    receta=receta,
                    perfil=perfil,
                    comida=comida,
                    comensales=datos.comensales,
                )

            except ComidaMenuInvalidaError as error:
                raise MenuInvalidoError(
                    f"Error en el día {comida.dia}, "
                    f"{comida.tipo_comida.value}: {error}"
                ) from error

            # Preparar una comida independiente.
            comida_guardada = MenuComida(
                dia=comida.dia,
                tipo_comida=comida.tipo_comida,
                receta_id=receta.id,
                instantanea=instantanea,
            )

            comidas_validadas.append(comida_guardada)

        # Crear el menú después de validar las comidas.
        menu = Menu(
            cuenta_id=cuenta_id,
            nombre=datos.nombre.strip(),
            cantidad_dias=datos.cantidad_dias,
            fecha_inicio=datos.fecha_inicio,
            comensales=datos.comensales,
            tamano_porcion=datos.tamano_porcion.value,
            comidas=comidas_validadas,
        )

        # Persistir todo en una única transacción.
        try:
            self.db.add(menu)
            self.db.commit()
            self.db.refresh(menu)

        except Exception:
            self.db.rollback()
            raise

        return menu
