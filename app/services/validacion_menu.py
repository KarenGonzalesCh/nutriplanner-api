
from app.models.perfil_alimentario import PerfilAlimentario
from app.models.receta import Receta
from app.schemas.menu import ComidaConfirmadaRequest
from app.services.compatibilidad_ingrediente import (
    es_ingrediente_compatible,
)
from app.services.escalado_cantidades import (
    escalar_cantidad_normal,
)


class ComidaMenuInvalidaError(ValueError):
    """La comida contiene ingredientes o sustituciones inválidos."""


def construir_instantanea_comida(
    receta: Receta,
    perfil: PerfilAlimentario,
    comida: ComidaConfirmadaRequest,
    comensales: int,
) -> dict:
    """
    Valida las sustituciones confirmadas y prepara una
    copia histórica de la receta.

    No guarda datos ni modifica la receta original.
    """

    if not receta.activa or receta.id != comida.receta_id:
        raise ComidaMenuInvalidaError(
            "La receta no está disponible"
        )

    tipos_permitidos = {
        relacion.tipo_comida
        for relacion in receta.tipos_comida
    }

    if comida.tipo_comida not in tipos_permitidos:
        raise ComidaMenuInvalidaError(
            "La receta no corresponde al tipo de comida"
        )

    if comensales <= 0:
        raise ComidaMenuInvalidaError(
            "La cantidad de comensales debe ser positiva"
        )

    if receta.porciones_base is None or receta.porciones_base <= 0:
        raise ComidaMenuInvalidaError(
            "La receta no tiene porciones base válidas"
        )

    elecciones = {
        item.receta_ingrediente_id: item.alternativa_id
        for item in comida.sustituciones
    }

    posiciones = {
        posicion.id: posicion
        for posicion in receta.ingredientes
    }

    if not set(elecciones).issubset(posiciones):
        raise ComidaMenuInvalidaError(
            "Hay sustituciones de ingredientes ajenos a la receta"
        )

    ingredientes = []

    for posicion in sorted(
        receta.ingredientes, key=lambda item: item.id
    ):
        original = posicion.ingrediente
        alternativa_id = elecciones.get(posicion.id)


        original_compatible = es_ingrediente_compatible(
            original, perfil
        )

        if alternativa_id is None:
            if not original_compatible:
                raise ComidaMenuInvalidaError(
                    f"Falta confirmar la sustitución "
                    f"de {original.nombre}"
                )

            elegido = original
            cantidad_base = posicion.cantidad
            unidad = posicion.unidad
            sustitucion = None

        else:
            alternativa = next(
                (
                    item
                    for item in posicion.alternativas
                    if item.id == alternativa_id
                ),
                None,
            )

            if alternativa is None:
                raise ComidaMenuInvalidaError(
                    "La alternativa no pertenece a esta receta"
                )

            elegido = alternativa.ingrediente_alternativo

            if not es_ingrediente_compatible(elegido, perfil):
                raise ComidaMenuInvalidaError(
                    f"La alternativa {elegido.nombre} "
                    "no es compatible con el perfil"
                )

            cantidad_base = alternativa.cantidad
            unidad = alternativa.unidad

            sustitucion = {
                "alternativa_id": alternativa.id,
                "ingrediente_original_id": original.id,
                "nombre_original": original.nombre,
            }


        cantidad = escalar_cantidad_normal(
            cantidad_base=cantidad_base,
            comensales=comensales,
            porciones_base=receta.porciones_base,
        )

        ingredientes.append({
            "receta_ingrediente_id": posicion.id,
            "ingrediente_id": elegido.id,
            "nombre": elegido.nombre,
            "cantidad": str(cantidad),
            "unidad": unidad,
            "sustitucion": sustitucion,
        })

    return {
        "receta_id": receta.id,
        "nombre_receta": receta.nombre,
        "pasos": receta.pasos,
        "tiempo_preparacion": receta.tiempo_preparacion,
        "dificultad": receta.dificultad.value,
        "porciones_base": receta.porciones_base,
        "comensales": comensales,
        "ingredientes": ingredientes,
    }
