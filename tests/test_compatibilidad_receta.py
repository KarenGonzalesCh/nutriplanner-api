from types import SimpleNamespace

from app.services.compatibilidad_receta import (
    EstadoCompatibilidad,
    evaluar_compatibilidad_receta,
)


def crear_ingrediente(id, categoria_id=1, alergias=None):
    return SimpleNamespace(
        id=id,
        categoria_id=categoria_id,
        alergias=alergias if alergias is not None else [],
    )


def crear_perfil(
    alergias=None,
    ingredientes_evitados=None,
    categorias_evitadas=None,
):
    return SimpleNamespace(
        alergias=alergias if alergias is not None else [],
        ingredientes_evitados=ingredientes_evitados if ingredientes_evitados is not None else [],
        categorias_evitadas=categorias_evitadas if categorias_evitadas is not None else [],
    )


def crear_posicion(ingrediente, alternativas=None):
    return SimpleNamespace(
        ingrediente=ingrediente,
        alternativas=[
            SimpleNamespace(ingrediente_alternativo=alternativa)
            for alternativa in (alternativas or [])
        ],
    )


def crear_receta(*posiciones):
    return SimpleNamespace(ingredientes=list(posiciones))


def test_receta_compatible():
    receta = crear_receta(
        crear_posicion(crear_ingrediente(1)),
        crear_posicion(crear_ingrediente(2)),
    )
    perfil = crear_perfil()

    resultado = evaluar_compatibilidad_receta(receta, perfil)

    assert resultado == EstadoCompatibilidad.COMPATIBLE


def test_receta_adaptable():
    leche = crear_ingrediente(1)
    bebida_vegetal = crear_ingrediente(2)

    receta = crear_receta(
        crear_posicion(leche, alternativas=[bebida_vegetal])
    )
    perfil = crear_perfil(ingredientes_evitados=[leche])

    resultado = evaluar_compatibilidad_receta(receta, perfil)

    assert resultado == EstadoCompatibilidad.ADAPTABLE


def test_receta_incompatible_sin_alternativas():
    leche = crear_ingrediente(1)

    receta = crear_receta(crear_posicion(leche))
    perfil = crear_perfil(ingredientes_evitados=[leche])

    resultado = evaluar_compatibilidad_receta(receta, perfil)

    assert resultado == EstadoCompatibilidad.INCOMPATIBLE


def test_varios_ingredientes_con_alternativas_validas():
    leche = crear_ingrediente(1)
    huevo = crear_ingrediente(2)
    bebida_vegetal = crear_ingrediente(3)
    sustituto_huevo = crear_ingrediente(4)

    receta = crear_receta(
        crear_posicion(leche, [bebida_vegetal]),
        crear_posicion(huevo, [sustituto_huevo]),
    )

    perfil = crear_perfil(
        ingredientes_evitados=[leche, huevo]
    )

    resultado = evaluar_compatibilidad_receta(receta, perfil)

    assert resultado == EstadoCompatibilidad.ADAPTABLE


def test_un_ingrediente_sin_alternativa_vuelve_incompatible_la_receta():
    leche = crear_ingrediente(1)
    huevo = crear_ingrediente(2)
    bebida_vegetal = crear_ingrediente(3)

    receta = crear_receta(
        crear_posicion(leche, [bebida_vegetal]),
        crear_posicion(huevo),
    )

    perfil = crear_perfil(
        ingredientes_evitados=[leche, huevo]
    )

    resultado = evaluar_compatibilidad_receta(receta, perfil)

    assert resultado == EstadoCompatibilidad.INCOMPATIBLE


def test_alternativa_que_incumple_otra_restriccion_no_es_valida():
    leche = crear_ingrediente(1, categoria_id=1)
    sustituto = crear_ingrediente(2, categoria_id=5)

    receta = crear_receta(
        crear_posicion(leche, alternativas=[sustituto])
    )

    perfil = crear_perfil(
        ingredientes_evitados=[leche],
        categorias_evitadas=[SimpleNamespace(id=5)],
    )

    resultado = evaluar_compatibilidad_receta(receta, perfil)

    assert resultado == EstadoCompatibilidad.INCOMPATIBLE
