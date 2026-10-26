from types import SimpleNamespace

from app.services.compatibilidad_ingrediente import es_ingrediente_compatible


def crear_ingrediente(id=1, categoria_id=10, alergias=None):
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
        ingredientes_evitados=(
            ingredientes_evitados if ingredientes_evitados is not None else []
        ),
        categorias_evitadas=(
            categorias_evitadas if categorias_evitadas is not None else []
        ),
    )


def test_ingrediente_sin_restricciones_es_compatible():
    ingrediente = crear_ingrediente()
    perfil = crear_perfil()

    assert es_ingrediente_compatible(ingrediente, perfil) is True


def test_ingrediente_con_alergia_es_incompatible():
    alergia = SimpleNamespace(id=5)
    ingrediente = crear_ingrediente(alergias=[alergia])
    perfil = crear_perfil(alergias=[alergia])

    assert es_ingrediente_compatible(ingrediente, perfil) is False


def test_ingrediente_evitado_es_incompatible():
    ingrediente = crear_ingrediente(id=3)
    perfil = crear_perfil(
        ingredientes_evitados=[SimpleNamespace(id=3)]
    )

    assert es_ingrediente_compatible(ingrediente, perfil) is False


def test_categoria_evitada_es_incompatible():
    ingrediente = crear_ingrediente(categoria_id=7)
    perfil = crear_perfil(
        categorias_evitadas=[SimpleNamespace(id=7)]
    )

    assert es_ingrediente_compatible(ingrediente, perfil) is False


def test_restricciones_no_coincidentes_permiten_ingrediente():
    ingrediente = crear_ingrediente(
        id=1,
        categoria_id=10,
        alergias=[SimpleNamespace(id=2)],
    )

    perfil = crear_perfil(
        alergias=[SimpleNamespace(id=3)],
        ingredientes_evitados=[SimpleNamespace(id=4)],
        categorias_evitadas=[SimpleNamespace(id=5)],
    )

    assert es_ingrediente_compatible(ingrediente, perfil) is True
