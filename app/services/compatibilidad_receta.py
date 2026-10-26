from enum import Enum

from app.models.receta import Receta
from app.models.perfil_alimentario import PerfilAlimentario
from app.services.compatibilidad_ingrediente import es_ingrediente_compatible


class EstadoCompatibilidad(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    ADAPTABLE = "ADAPTABLE"
    INCOMPATIBLE = "INCOMPATIBLE"


def evaluar_compatibilidad_receta(
    receta: Receta,
    perfil: PerfilAlimentario,
) -> EstadoCompatibilidad:
    """Clasifica una receta según las restricciones y alternativas disponibles."""

    necesita_sustituciones = False

    for receta_ingrediente in receta.ingredientes:
        ingrediente_original = receta_ingrediente.ingrediente

        # El ingrediente original cumple las restricciones.
        if es_ingrediente_compatible(ingrediente_original, perfil):
            continue

        necesita_sustituciones = True

        # Buscar al menos una alternativa compatible.
        tiene_alternativa_valida = any(
            es_ingrediente_compatible(
                alternativa.ingrediente_alternativo,
                perfil
            )
            for alternativa in receta_ingrediente.alternativas
        )

        # Basta un ingrediente sin alternativa para rechazar la receta.
        if not tiene_alternativa_valida:
            return EstadoCompatibilidad.INCOMPATIBLE

    if necesita_sustituciones:
        return EstadoCompatibilidad.ADAPTABLE

    return EstadoCompatibilidad.COMPATIBLE
