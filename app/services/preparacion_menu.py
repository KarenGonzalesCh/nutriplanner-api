
from app.models.receta import Receta

from app.schemas.menu import (
    ComidaPropuestaResponse,
    IngredienteEscaladoResponse,
    PropuestaMenuResponse,
)

from app.services.escalado_cantidades import (
    escalar_ingredientes_receta,
)

from app.services.generador_menu import PropuestaMenu


def preparar_respuesta_menu(
    propuesta: PropuestaMenu,
    recetas: list[Receta],
    comensales: int,
) -> PropuestaMenuResponse:
    """
    Prepara la respuesta de una propuesta de menú.

    Escala las cantidades de recetas que no requieren
    sustituciones pendientes.

    No modifica las recetas almacenadas ni guarda el menú.
    """

    if comensales <= 0:
        raise ValueError(
            "La cantidad de comensales debe ser positiva"
        )

    recetas_por_id = {
        receta.id: receta
        for receta in recetas
    }

    comidas_respuesta = []

    for comida in propuesta.comidas:
        ingredientes = []

        if comida.receta_id is not None:
            receta = recetas_por_id.get(comida.receta_id)

            if receta is None:
                raise ValueError(
                    f"No se encontró la receta {comida.receta_id}"
                )

            # No mostramos ingredientes originales como si
            # fueran compatibles cuando falta una sustitución.
            if not comida.requiere_sustituciones:
                ingredientes_escalados = escalar_ingredientes_receta(
                    receta=receta,
                    comensales=comensales,
                )

                ingredientes = [
                    IngredienteEscaladoResponse(
                        receta_ingrediente_id=ingrediente.receta_ingrediente_id,
                        ingrediente_id=ingrediente.ingrediente_id,
                        cantidad=ingrediente.cantidad,
                        unidad=ingrediente.unidad,
                    )
                    for ingrediente in ingredientes_escalados
                ]

        comidas_respuesta.append(
            ComidaPropuestaResponse(
                dia=comida.dia,
                tipo_comida=comida.tipo_comida,
                receta_id=comida.receta_id,
                tiene_conflicto_flexible=comida.tiene_conflicto_flexible,
                requiere_sustituciones=comida.requiere_sustituciones,
                ingredientes=ingredientes,
            )
        )

    return PropuestaMenuResponse(
        comidas=comidas_respuesta,
        estructura_completa=propuesta.completa,
    )
