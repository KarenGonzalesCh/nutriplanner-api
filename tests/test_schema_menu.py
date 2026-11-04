import pytest
from pydantic import ValidationError

from app.core.enums import TipoComida
from app.schemas.menu import GenerarMenuRequest, TamanoPorcion


def test_solicitud_valida():
    solicitud = GenerarMenuRequest(
        cantidad_dias=3,
        tipos_comida=[
            TipoComida.ALMUERZO,
            TipoComida.CENA,
        ],
        comensales=2,
    )

    assert solicitud.cantidad_dias == 3
    assert solicitud.comensales == 2
    assert solicitud.tamano_porcion == TamanoPorcion.NORMAL


@pytest.mark.parametrize("dias", [0, 8, -1])
def test_rechaza_cantidad_dias_invalida(dias):
    with pytest.raises(ValidationError):
        GenerarMenuRequest(
            cantidad_dias=dias,
            tipos_comida=[TipoComida.CENA],
            comensales=2,
        )


def test_rechaza_comidas_duplicadas():
    with pytest.raises(ValidationError):
        GenerarMenuRequest(
            cantidad_dias=2,
            tipos_comida=[
                TipoComida.CENA,
                TipoComida.CENA,
            ],
            comensales=2,
        )


def test_rechaza_comensales_invalidos():
    with pytest.raises(ValidationError):
        GenerarMenuRequest(
            cantidad_dias=2,
            tipos_comida=[TipoComida.CENA],
            comensales=0,
        )


def test_rechaza_restricciones_temporales():
    with pytest.raises(ValidationError):
        GenerarMenuRequest(
            cantidad_dias=2,
            tipos_comida=[TipoComida.CENA],
            comensales=2,
            ingredientes_evitados_ids=[5],
        )


def test_rechaza_menu_sin_comidas():
    with pytest.raises(ValidationError):
        GenerarMenuRequest(
            cantidad_dias=2,
            tipos_comida=[],
            comensales=2,
        )

@pytest.mark.parametrize(
    "tamano",
    [TamanoPorcion.PEQUENA, TamanoPorcion.GRANDE],
)
def test_rechaza_tamanos_no_implementados(tamano):
    with pytest.raises(ValidationError):
        GenerarMenuRequest(
            cantidad_dias=2,
            tipos_comida=[TipoComida.ALMUERZO],
            comensales=2,
            tamano_porcion=tamano,
        )