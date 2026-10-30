from decimal import Decimal


def escalar_cantidad_normal(
    cantidad_base: float | int | Decimal,
    comensales: int,
    porciones_base: int,
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

    if porciones_base <= 0:
        raise ValueError(
            "Las porciones base deben ser positivas"
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