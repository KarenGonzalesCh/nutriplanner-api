from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.enums import TipoComida
from app.services.generador_menu import (
    ComidaPropuesta,
    PropuestaMenu,
)
from app.services.preparacion_menu import preparar_respuesta_menu

def crear_receta_ejemplo(porciones_base=1):
    return SimpleNamespace(
        id=2,
        porciones_base=porciones_base,
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


def test_preparar_menu_con_ingredientes_escalados():
    receta = crear_receta_ejemplo()

    propuesta = PropuestaMenu(
        comidas=[
            ComidaPropuesta(
                dia=1,
                tipo_comida=TipoComida.ALMUERZO,
                receta_id=2,
            ),
        ]
    )

    resultado = preparar_respuesta_menu(
        propuesta=propuesta,
        recetas=[receta],
        comensales=3,
    )

    comida = resultado.comidas[0]

    assert resultado.estructura_completa
    assert comida.receta_id == 2
    assert len(comida.ingredientes) == 2
    assert comida.ingredientes[0].cantidad == Decimal("450")
    assert comida.ingredientes[1].cantidad == Decimal("600")

    # Las cantidades originales no se modifican.
    assert receta.ingredientes[0].cantidad == 150
    assert receta.ingredientes[1].cantidad == 200


def test_no_mostrar_ingredientes_con_sustitucion_pendiente():
    receta = crear_receta_ejemplo()

    propuesta = PropuestaMenu(
        comidas=[
            ComidaPropuesta(
                dia=1,
                tipo_comida=TipoComida.ALMUERZO,
                receta_id=2,
                requiere_sustituciones=True,
            ),
        ]
    )

    resultado = preparar_respuesta_menu(
        propuesta=propuesta,
        recetas=[receta],
        comensales=2,
    )

    comida = resultado.comidas[0]

    assert comida.requiere_sustituciones
    assert comida.ingredientes == []
    assert resultado.estructura_completa


def test_preparar_menu_con_espacio_sin_receta():
    propuesta = PropuestaMenu(
        comidas=[
            ComidaPropuesta(
                dia=1,
                tipo_comida=TipoComida.CENA,
                receta_id=None,
            ),
        ]
    )

    resultado = preparar_respuesta_menu(
        propuesta=propuesta,
        recetas=[],
        comensales=2,
    )

    assert not resultado.estructura_completa
    assert resultado.comidas[0].receta_id is None
    assert resultado.comidas[0].ingredientes == []


def test_rechazar_receta_no_encontrada():
    propuesta = PropuestaMenu(
        comidas=[
            ComidaPropuesta(
                dia=1,
                tipo_comida=TipoComida.ALMUERZO,
                receta_id=99,
            ),
        ]
    )

    with pytest.raises(ValueError, match="No se encontró la receta"):
        preparar_respuesta_menu(
            propuesta=propuesta,
            recetas=[],
            comensales=2,
        )


def test_rechazar_receta_sin_porciones_base():
    receta = crear_receta_ejemplo(porciones_base=None)

    propuesta = PropuestaMenu(
        comidas=[
            ComidaPropuesta(
                dia=1,
                tipo_comida=TipoComida.ALMUERZO,
                receta_id=2,
            ),
        ]
    )

    with pytest.raises(ValueError, match="porciones base"):
        preparar_respuesta_menu(
            propuesta=propuesta,
            recetas=[receta],
            comensales=2,
        )


def test_rechazar_comensales_invalidos():
    propuesta = PropuestaMenu(comidas=[])

    with pytest.raises(ValueError, match="comensales"):
        preparar_respuesta_menu(
            propuesta=propuesta,
            recetas=[],
            comensales=0,
        )
