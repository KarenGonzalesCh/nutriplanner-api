from dataclasses import dataclass
from decimal import Decimal

from app.models.receta import Receta

def escalar_cantidad_normal(
    cantidad_base: float | int | Decimal,
    comensales: int,
    porciones_base: int | None,
) -> Decimal:
    """
    Escala una cantidad para el número de comensales.

    Solo contempla tamaño de porción NORMAL.
    No aplica redondeos ni conversiones de unidades.
    """

    if comensales <= 0:
        raise ValueError(
            "La cantidad de comensales debe ser positiva"
        )

    if porciones_base is None or porciones_base <= 0:
        raise ValueError(
           "La receta debe tener porciones base definidas y positivas"
        )

    cantidad = Decimal(str(cantidad_base))

    if not cantidad.is_finite() or cantidad <= 0:
        raise ValueError(
            "La cantidad base debe ser positiva y finita"
        )

    return (
        cantidad
        * Decimal(comensales)
        / Decimal(porciones_base)
    )

@dataclass(frozen=True)
class IngredienteEscalado:
    receta_ingrediente_id: int
    ingrediente_id: int
    cantidad: Decimal
    unidad: str


def escalar_ingredientes_receta(
    receta: Receta,
    comensales: int,
) -> list[IngredienteEscalado]:
    """Calcula las cantidades para los comensales indicados."""

    if comensales <= 0:
        raise ValueError(
            "La cantidad de comensales debe ser positiva"
        )

    if receta.porciones_base is None or receta.porciones_base <= 0:
        raise ValueError(
            "La receta debe tener porciones base definidas y positivas"
        )

    resultado = []

    for posicion in receta.ingredientes:
        cantidad_ajustada = escalar_cantidad_normal(
            cantidad_base=posicion.cantidad,
            comensales=comensales,
            porciones_base=receta.porciones_base,
        )

        resultado.append(
            IngredienteEscalado(
                receta_ingrediente_id=posicion.id,
                ingrediente_id=posicion.ingrediente_id,
                cantidad=cantidad_ajustada,
                unidad=posicion.unidad,
            )
        )

    return resultado