from app.models.receta import Receta
from app.models.perfil_alimentario import PerfilAlimentario

from app.services.compatibilidad_ingrediente import (
    es_ingrediente_compatible,
)
from app.services.compatibilidad_receta import (
    evaluar_compatibilidad_receta,
)

from app.schemas.compatibilidad_receta import (
    AlternativaDisponibleResponse,
    IngredienteRestringidoResponse,
    CompatibilidadRecetaResponse,
)


def preparar_detalle_compatibilidad(
    receta: Receta,
    perfil: PerfilAlimentario,
) -> CompatibilidadRecetaResponse:
    """Prepara el estado y las alternativas válidas de una receta."""

    estado = evaluar_compatibilidad_receta(receta, perfil)

    ingredientes_restringidos = []

    for posicion in receta.ingredientes:
        ingrediente = posicion.ingrediente

        # Los ingredientes permitidos no necesitan sustitución.
        if es_ingrediente_compatible(ingrediente, perfil):
            continue

        alternativas_validas = []

        for alternativa in posicion.alternativas:
            sustituto = alternativa.ingrediente_alternativo

            if not es_ingrediente_compatible(sustituto, perfil):
                continue

            alternativas_validas.append(
                AlternativaDisponibleResponse(
                    id=alternativa.id,
                    ingrediente_id=sustituto.id,
                    nombre=sustituto.nombre,
                    cantidad=alternativa.cantidad,
                    unidad=alternativa.unidad,
                )
            )

        ingredientes_restringidos.append(
            IngredienteRestringidoResponse(
                receta_ingrediente_id=posicion.id,
                ingrediente_id=ingrediente.id,
                nombre=ingrediente.nombre,
                alternativas_validas=alternativas_validas,
            )
        )

    return CompatibilidadRecetaResponse(
        receta_id=receta.id,
        nombre=receta.nombre,
        estado_compatibilidad=estado,
        ingredientes_restringidos=ingredientes_restringidos,
    )
