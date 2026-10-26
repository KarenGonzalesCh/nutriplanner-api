from app.models.ingrediente import Ingrediente
from app.models.perfil_alimentario import PerfilAlimentario


def cumple_restriccion_alergias(
    ingrediente: Ingrediente,
    perfil: PerfilAlimentario,
) -> bool:
    """Verifica que el ingrediente no contenga alérgenos del perfil."""

    alergias_usuario = {
        alergia.id for alergia in perfil.alergias
    }

    return not any(
        alergia.id in alergias_usuario
        for alergia in ingrediente.alergias
    )


def cumple_restriccion_ingredientes(
    ingrediente: Ingrediente,
    perfil: PerfilAlimentario,
) -> bool:
    """Verifica que el ingrediente no esté entre los evitados."""

    ingredientes_evitados = {
        item.id for item in perfil.ingredientes_evitados
    }

    return ingrediente.id not in ingredientes_evitados


def cumple_restriccion_categorias(
    ingrediente: Ingrediente,
    perfil: PerfilAlimentario,
) -> bool:
    """Verifica que la categoría del ingrediente no esté evitada."""

    categorias_evitadas = {
        categoria.id for categoria in perfil.categorias_evitadas
    }

    return ingrediente.categoria_id not in categorias_evitadas


def es_ingrediente_compatible(
    ingrediente: Ingrediente,
    perfil: PerfilAlimentario,
) -> bool:
    """Comprueba todas las restricciones alimentarias del perfil."""

    return (
        cumple_restriccion_alergias(ingrediente, perfil)
        and cumple_restriccion_ingredientes(ingrediente, perfil)
        and cumple_restriccion_categorias(ingrediente, perfil)
    )
