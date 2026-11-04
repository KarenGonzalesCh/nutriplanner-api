from types import SimpleNamespace

import pytest

from app.core.enums import NivelDificultad, TipoComida
from app.services.generador_menu import (
    filtrar_candidatas_basicas,
    CandidataMenu,
    seleccionar_candidata,
    armar_propuesta_menu,
)

def test_prioriza_receta_distinta_sin_conflictos():
    candidatas = [
        CandidataMenu(1, True),
        CandidataMenu(2, False),
    ]

    resultado = seleccionar_candidata(candidatas, set())

    assert resultado.receta_id == 2


def test_prioriza_distinta_flexible_antes_de_repetir():
    candidatas = [
        CandidataMenu(1, False),
        CandidataMenu(2, True),
    ]

    resultado = seleccionar_candidata(candidatas, {1})

    assert resultado.receta_id == 2


def test_prioriza_repetida_sin_conflictos():
    candidatas = [
        CandidataMenu(1, True),
        CandidataMenu(2, False),
    ]

    resultado = seleccionar_candidata(candidatas, {1, 2})

    assert resultado.receta_id == 2


def test_prioriza_distinta_aunque_ambas_tengan_conflictos():
    candidatas = [
        CandidataMenu(1, True),
        CandidataMenu(2, True),
    ]

    resultado = seleccionar_candidata(candidatas, {1})

    assert resultado.receta_id == 2


def test_sin_candidatas_devuelve_none():
    resultado = seleccionar_candidata([], set())

    assert resultado is None


def test_seleccion_no_modifica_recetas_utilizadas():
    utilizadas = {1}

    seleccionar_candidata(
        [CandidataMenu(2, False)],
        utilizadas,
    )

    assert utilizadas == {1}


def crear_receta(
    dificultad,
    tipos_comida,
    activa=True,
):
    return SimpleNamespace(
        activa=activa,
        dificultad=dificultad,
        tipos_comida=[
            SimpleNamespace(tipo_comida=tipo)
            for tipo in tipos_comida
        ],
    )


@pytest.mark.parametrize(
    "nivel_usuario,dificultad_receta,esperada",
    [
        (NivelDificultad.PRINCIPIANTE,
         NivelDificultad.PRINCIPIANTE, True),
        (NivelDificultad.PRINCIPIANTE,
         NivelDificultad.INTERMEDIO, False),
        (NivelDificultad.PRINCIPIANTE,
         NivelDificultad.AVANZADO, False),
        (NivelDificultad.INTERMEDIO,
         NivelDificultad.PRINCIPIANTE, True),
        (NivelDificultad.INTERMEDIO,
         NivelDificultad.INTERMEDIO, True),
        (NivelDificultad.INTERMEDIO,
         NivelDificultad.AVANZADO, False),
        (NivelDificultad.AVANZADO,
         NivelDificultad.PRINCIPIANTE, True),
        (NivelDificultad.AVANZADO,
         NivelDificultad.INTERMEDIO, True),
        (NivelDificultad.AVANZADO,
         NivelDificultad.AVANZADO, True),
    ],
)
def test_filtrado_por_nivel(
    nivel_usuario,
    dificultad_receta,
    esperada,
):
    perfil = SimpleNamespace(
        nivel_culinario=nivel_usuario
    )

    receta = crear_receta(
        dificultad=dificultad_receta,
        tipos_comida=[TipoComida.ALMUERZO],
    )

    resultado = filtrar_candidatas_basicas(
        [receta],
        perfil,
        TipoComida.ALMUERZO,
    )

    assert (receta in resultado) is esperada


def test_filtrado_por_tipo_comida():
    perfil = SimpleNamespace(
        nivel_culinario=NivelDificultad.AVANZADO
    )

    receta = crear_receta(
        dificultad=NivelDificultad.PRINCIPIANTE,
        tipos_comida=[TipoComida.DESAYUNO],
    )

    resultado = filtrar_candidatas_basicas(
        [receta],
        perfil,
        TipoComida.CENA,
    )

    assert resultado == []


def test_receta_con_multiples_tipos_comida():
    perfil = SimpleNamespace(
        nivel_culinario=NivelDificultad.INTERMEDIO
    )

    receta = crear_receta(
        dificultad=NivelDificultad.INTERMEDIO,
        tipos_comida=[
            TipoComida.ALMUERZO,
            TipoComida.CENA,
        ],
    )

    resultado = filtrar_candidatas_basicas(
        [receta],
        perfil,
        TipoComida.CENA,
    )

    assert resultado == [receta]


def test_receta_inactiva_no_es_candidata():
    perfil = SimpleNamespace(
        nivel_culinario=NivelDificultad.AVANZADO
    )

    receta = crear_receta(
        dificultad=NivelDificultad.PRINCIPIANTE,
        tipos_comida=[TipoComida.CENA],
        activa=False,
    )

    resultado = filtrar_candidatas_basicas(
        [receta],
        perfil,
        TipoComida.CENA,
    )

    assert resultado == []

def test_generar_menu_de_un_dia():
    propuesta = armar_propuesta_menu(
        cantidad_dias=1,
        tipos_comida=[TipoComida.ALMUERZO, TipoComida.CENA],
        candidatas_por_tipo={
            TipoComida.ALMUERZO: [CandidataMenu(1, False)],
            TipoComida.CENA: [CandidataMenu(2, False)],
        },
    )

    assert len(propuesta.comidas) == 2
    assert propuesta.completa
    assert [c.receta_id for c in propuesta.comidas] == [1, 2]


def test_generar_tres_dias_prioriza_variedad():
    propuesta = armar_propuesta_menu(
        cantidad_dias=3,
        tipos_comida=[TipoComida.ALMUERZO],
        candidatas_por_tipo={
            TipoComida.ALMUERZO: [
                CandidataMenu(1, False),
                CandidataMenu(2, False),
                CandidataMenu(3, True),
            ],
        },
    )

    ids = [comida.receta_id for comida in propuesta.comidas]

    assert len(set(ids)) == 3
    assert propuesta.completa
    assert sum(c.tiene_conflicto_flexible for c in propuesta.comidas) == 1


def test_evitar_repeticion_entre_tipos_de_comida():
    propuesta = armar_propuesta_menu(
        cantidad_dias=1,
        tipos_comida=[TipoComida.ALMUERZO, TipoComida.CENA],
        candidatas_por_tipo={
            TipoComida.ALMUERZO: [
                CandidataMenu(1, False),
                CandidataMenu(2, False),
            ],
            TipoComida.CENA: [
                CandidataMenu(1, False),
            ],
        },
    )

    assert [c.receta_id for c in propuesta.comidas] == [2, 1]


def test_repetir_receta_cuando_se_agotan_opciones():
    propuesta = armar_propuesta_menu(
        cantidad_dias=4,
        tipos_comida=[TipoComida.DESAYUNO],
        candidatas_por_tipo={
            TipoComida.DESAYUNO: [
                CandidataMenu(1, False),
                CandidataMenu(2, False),
                CandidataMenu(3, True),
            ],
        },
    )

    ids = [comida.receta_id for comida in propuesta.comidas]

    assert len(ids) == 4
    assert len(set(ids)) == 3
    assert propuesta.completa


def test_menu_parcial_sin_recetas_disponibles():
    propuesta = armar_propuesta_menu(
        cantidad_dias=2,
        tipos_comida=[TipoComida.CENA],
        candidatas_por_tipo={TipoComida.CENA: []},
    )

    assert not propuesta.completa
    assert all(c.receta_id is None for c in propuesta.comidas)


@pytest.mark.parametrize("cantidad_dias", [0, 8, -1])
def test_cantidad_dias_invalida(cantidad_dias):
    with pytest.raises(ValueError):
        armar_propuesta_menu(
            cantidad_dias=cantidad_dias,
            tipos_comida=[TipoComida.CENA],
            candidatas_por_tipo={},
        )


def test_no_permite_menu_sin_comidas():
    with pytest.raises(ValueError):
        armar_propuesta_menu(
            cantidad_dias=1,
            tipos_comida=[],
            candidatas_por_tipo={},
        )


def test_no_permite_tipos_de_comida_duplicados():
    with pytest.raises(ValueError):
        armar_propuesta_menu(
            cantidad_dias=1,
            tipos_comida=[TipoComida.CENA, TipoComida.CENA],
            candidatas_por_tipo={},
        )

def test_reasigna_recetas_para_evitar_repeticiones():
    propuesta = armar_propuesta_menu(
        cantidad_dias=1,
        tipos_comida=[
            TipoComida.ALMUERZO,
            TipoComida.CENA,
        ],
        candidatas_por_tipo={
            TipoComida.ALMUERZO: [
                CandidataMenu(1, False),
                CandidataMenu(2, True),
            ],
            TipoComida.CENA: [
                CandidataMenu(1, False),
            ],
        },
    )

    ids = [comida.receta_id for comida in propuesta.comidas]

    assert ids == [2, 1]
    assert propuesta.completa
    assert propuesta.comidas[0].tiene_conflicto_flexible
    assert not propuesta.comidas[1].tiene_conflicto_flexible

def test_minimiza_conflictos_flexibles_en_menu_completo():
    propuesta = armar_propuesta_menu(
        cantidad_dias=1,
        tipos_comida=[
            TipoComida.DESAYUNO,
            TipoComida.ALMUERZO,
            TipoComida.CENA,
        ],
        candidatas_por_tipo={
            TipoComida.DESAYUNO: [
                CandidataMenu(11, True),
                CandidataMenu(12, False),
            ],
            TipoComida.ALMUERZO: [
                CandidataMenu(10, True),
                CandidataMenu(14, True),
            ],
            TipoComida.CENA: [
                CandidataMenu(10, False),
                CandidataMenu(12, False),
            ],
        },
    )

    ids = [comida.receta_id for comida in propuesta.comidas]
    advertencias = sum(
        comida.tiene_conflicto_flexible
        for comida in propuesta.comidas
    )

    assert propuesta.completa
    assert len(set(ids)) == 3
    assert advertencias == 1