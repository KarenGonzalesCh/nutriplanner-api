
import pytest
from pydantic import ValidationError

from app.schemas.menu import GuardarMenuRequest


def datos_menu_valido():
    return {
        "nombre": "Mi menú semanal",
        "cantidad_dias": 2,
        "comensales": 1,
        "tamano_porcion": "NORMAL",
        "comidas": [
            {
                "dia": 1,
                "tipo_comida": "DESAYUNO",
                "receta_id": 10,
                "sustituciones": [
                    {
                        "receta_ingrediente_id": 5,
                        "alternativa_id": 20,
                    }
                ],
            },
            {
                "dia": 2,
                "tipo_comida": "DESAYUNO",
                "receta_id": 10,
                "sustituciones": [
                    {
                        "receta_ingrediente_id": 5,
                        "alternativa_id": 21,
                    }
                ],
            },
        ],
    }


def test_permite_sustituciones_distintas_por_comida():
    datos = datos_menu_valido()

    menu = GuardarMenuRequest.model_validate(datos)

    assert len(menu.comidas) == 2
    assert menu.comidas[0].receta_id == 10
    assert menu.comidas[1].receta_id == 10

    assert (
        menu.comidas[0].sustituciones[0].alternativa_id
        == 20
    )
    assert (
        menu.comidas[1].sustituciones[0].alternativa_id
        == 21
    )


def test_rechaza_comida_duplicada_en_el_mismo_dia():
    datos = datos_menu_valido()

    datos["comidas"][1]["dia"] = 1

    with pytest.raises(ValidationError):
        GuardarMenuRequest.model_validate(datos)


def test_rechaza_sustituciones_duplicadas():
    datos = datos_menu_valido()

    datos["comidas"][0]["sustituciones"].append(
        {
            "receta_ingrediente_id": 5,
            "alternativa_id": 22,
        }
    )

    with pytest.raises(ValidationError):
        GuardarMenuRequest.model_validate(datos)


def test_rechaza_comensales_invalidos():
    datos = datos_menu_valido()
    datos["comensales"] = 0

    with pytest.raises(ValidationError):
        GuardarMenuRequest.model_validate(datos)
