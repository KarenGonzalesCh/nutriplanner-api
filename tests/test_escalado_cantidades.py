from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.services.escalado_cantidades import (
    escalar_cantidad_normal,
    escalar_ingredientes_receta,
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
        (2, None),
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

def test_escalar_todos_los_ingredientes():
    receta = SimpleNamespace(
        porciones_base=2,
        ingredientes=[
            SimpleNamespace(
                id=10,
                ingrediente_id=1,
                cantidad=150,
                unidad="g",
            ),
            SimpleNamespace(
                id=11,
                ingrediente_id=2,
                cantidad=200,
                unidad="g",
            ),
        ],
    )

    resultado = escalar_ingredientes_receta(receta, comensales=4)

    assert len(resultado) == 2
    assert resultado[0].cantidad == Decimal("300")
    assert resultado[1].cantidad == Decimal("400")
    assert resultado[0].receta_ingrediente_id == 10

    # No altera las cantidades originales.
    assert receta.ingredientes[0].cantidad == 150
    assert receta.ingredientes[1].cantidad == 200


def test_escalar_receta_sin_porciones_base():
    receta = SimpleNamespace(
        porciones_base=None,
        ingredientes=[
            SimpleNamespace(
                id=10,
                ingrediente_id=1,
                cantidad=150,
                unidad="g",
            ),
        ],
    )

    with pytest.raises(ValueError):
        escalar_ingredientes_receta(receta, comensales=2)


def test_escalar_receta_rechaza_comensales_invalidos():
    receta = SimpleNamespace(
        porciones_base=2,
        ingredientes=[],
    )

    with pytest.raises(ValueError):
        escalar_ingredientes_receta(receta, comensales=0)