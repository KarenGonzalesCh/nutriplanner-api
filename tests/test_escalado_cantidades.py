from decimal import Decimal

import pytest

from app.services.escalado_cantidades import (
    escalar_cantidad_normal,
)


def test_escalar_para_mas_comensales():
    resultado = escalar_cantidad_normal(
        cantidad_base=200,
        comensales=4,
        porciones_base=2,
    )

    assert resultado == Decimal("400")


def test_escalar_para_menos_comensales():
    resultado = escalar_cantidad_normal(
        cantidad_base=200,
        comensales=1,
        porciones_base=2,
    )

    assert resultado == Decimal("100")


def test_mantener_cantidad_original():
    resultado = escalar_cantidad_normal(
        cantidad_base=150,
        comensales=2,
        porciones_base=2,
    )

    assert resultado == Decimal("150")


def test_escalar_cantidad_de_alternativa():
    resultado = escalar_cantidad_normal(
        cantidad_base=150,
        comensales=3,
        porciones_base=2,
    )

    assert resultado == Decimal("225")


@pytest.mark.parametrize(
    "comensales,porciones_base",
    [
        (0, 2),
        (-1, 2),
        (2, 0),
        (2, -1),
    ],
)
def test_rechazar_parametros_invalidos(
    comensales,
    porciones_base,
):
    with pytest.raises(ValueError):
        escalar_cantidad_normal(
            cantidad_base=100,
            comensales=comensales,
            porciones_base=porciones_base,
        )


@pytest.mark.parametrize("cantidad", [0, -5, float("nan")])
def test_rechazar_cantidades_invalidas(cantidad):
    with pytest.raises(ValueError):
        escalar_cantidad_normal(
            cantidad_base=cantidad,
            comensales=2,
            porciones_base=2,
        )