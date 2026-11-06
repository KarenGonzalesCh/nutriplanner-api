
from types import SimpleNamespace as Objeto

import pytest

from app.core.enums import NivelDificultad, TipoComida
from app.schemas.menu import ComidaConfirmadaRequest
from app.services.validacion_menu import (
    ComidaMenuInvalidaError,
    construir_instantanea_comida,
)


def preparar_escenario():
    """Receta con leche restringida y alternativa vegetal."""

    leche = Objeto(
        id=1,
        nombre="Leche",
        categoria_id=1,
        alergias=[],
    )

    leche_coco = Objeto(
        id=2,
        nombre="Leche de coco",
        categoria_id=2,
        alergias=[],
    )

    alternativa = Objeto(
        id=10,
        ingrediente_alternativo=leche_coco,
        cantidad=200,
        unidad="ml",
    )

    posicion = Objeto(
        id=5,
        ingrediente=leche,
        cantidad=200,
        unidad="ml",
        alternativas=[alternativa],
    )

    receta = Objeto(
        id=100,
        nombre="Avena con banana",
        pasos="Preparar y servir.",
        tiempo_preparacion=10,
        dificultad=NivelDificultad.PRINCIPIANTE,
        porciones_base=1,
        activa=True,
        ingredientes=[posicion],
        tipos_comida=[
            Objeto(tipo_comida=TipoComida.DESAYUNO)
        ],
    )

    perfil = Objeto(
        alergias=[],
        ingredientes_evitados=[leche],
        categorias_evitadas=[],
    )

    return receta, perfil


def crear_comida(sustituciones):
    return ComidaConfirmadaRequest(
        dia=1,
        tipo_comida=TipoComida.DESAYUNO,
        receta_id=100,
        sustituciones=sustituciones,
    )


def test_rechaza_sustitucion_pendiente():
    receta, perfil = preparar_escenario()
    comida = crear_comida([])

    with pytest.raises(
        ComidaMenuInvalidaError,
        match="Falta confirmar",
    ):
        construir_instantanea_comida(
            receta, perfil, comida, comensales=1
        )


def test_aplica_sustitucion_y_escala_cantidad():
    receta, perfil = preparar_escenario()

    comida = crear_comida([
        {
            "receta_ingrediente_id": 5,
            "alternativa_id": 10,
        }
    ])

    resultado = construir_instantanea_comida(
        receta, perfil, comida, comensales=2
    )

    ingrediente = resultado["ingredientes"][0]

    assert ingrediente["nombre"] == "Leche de coco"
    assert ingrediente["ingrediente_id"] == 2
    assert ingrediente["cantidad"] == "400"
    assert ingrediente["unidad"] == "ml"

    assert ingrediente["sustitucion"]["alternativa_id"] == 10
    assert ingrediente["sustitucion"]["nombre_original"] == "Leche"

    # La receta original no debe modificarse.
    assert receta.ingredientes[0].ingrediente.nombre == "Leche"


def test_rechaza_alternativa_inexistente():
    receta, perfil = preparar_escenario()

    comida = crear_comida([
        {
            "receta_ingrediente_id": 5,
            "alternativa_id": 999,
        }
    ])

    with pytest.raises(
        ComidaMenuInvalidaError,
        match="no pertenece",
    ):
        construir_instantanea_comida(
            receta, perfil, comida, comensales=1
        )



def test_permite_sustitucion_voluntaria():
    receta, perfil = preparar_escenario()

    # La leche no está restringida.
    perfil.ingredientes_evitados = []

    comida = crear_comida([
        {
            "receta_ingrediente_id": 5,
            "alternativa_id": 10,
        }
    ])

    resultado = construir_instantanea_comida(
        receta, perfil, comida, comensales=1
    )

    ingrediente = resultado["ingredientes"][0]

    assert ingrediente["nombre"] == "Leche de coco"
    assert ingrediente["ingrediente_id"] == 2
    assert ingrediente["cantidad"] == "200"
    assert ingrediente["unidad"] == "ml"
    assert ingrediente["sustitucion"]["alternativa_id"] == 10

    # Verificación que la receta original no se modificó.
    assert receta.ingredientes[0].ingrediente.nombre == "Leche"

