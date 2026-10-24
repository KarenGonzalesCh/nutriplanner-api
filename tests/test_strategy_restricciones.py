
from app.core.enums import NivelDificultad
from app.models.alergia import Alergia
from app.models.ingrediente import Ingrediente
from app.models.perfil_alimentario import PerfilAlimentario
from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente

from app.strategies.restriccion_alergias import RestriccionAlergiasStrategy
from app.strategies.restriccion_ingredientes import RestriccionIngredientesStrategy
from app.models.categoria_alimento import CategoriaAlimento
from app.strategies.restriccion_categorias import RestriccionCategoriasStrategy
from app.services.evaluador_restricciones import crear_evaluador_restricciones

def crear_receta_con_ingrediente(ingrediente):
    receta = Receta(
        nombre="Receta de prueba",
        pasos="Preparar los ingredientes",
        tiempo_preparacion=15,
        dificultad=NivelDificultad.PRINCIPIANTE,
    )

    receta.ingredientes.append(
        RecetaIngrediente(
            ingrediente=ingrediente,
            cantidad=100,
            unidad="g",
        )
    )

    return receta


def test_alergias_rechaza_receta_incompatible():
    alergia_leche = Alergia(id=1, nombre="Leche")

    queso = Ingrediente(
        id=1,
        nombre="Queso",
        categoria_id=1,
    )
    queso.alergias.append(alergia_leche)

    receta = crear_receta_con_ingrediente(queso)

    perfil = PerfilAlimentario(
        cuenta_id=1,
        nivel_culinario=NivelDificultad.PRINCIPIANTE,
    )
    perfil.alergias.append(alergia_leche)

    estrategia = RestriccionAlergiasStrategy()

    assert estrategia.es_compatible(receta, perfil) is False


def test_alergias_acepta_receta_compatible():
    arroz = Ingrediente(
        id=2,
        nombre="Arroz",
        categoria_id=2,
    )

    receta = crear_receta_con_ingrediente(arroz)

    perfil = PerfilAlimentario(
        cuenta_id=1,
        nivel_culinario=NivelDificultad.PRINCIPIANTE,
    )
    perfil.alergias.append(Alergia(id=1, nombre="Leche"))

    estrategia = RestriccionAlergiasStrategy()

    assert estrategia.es_compatible(receta, perfil) is True


def test_ingredientes_rechaza_receta_incompatible():
    tomate = Ingrediente(
        id=1,
        nombre="Tomate",
        categoria_id=1,
    )

    receta = crear_receta_con_ingrediente(tomate)

    perfil = PerfilAlimentario(
        cuenta_id=1,
        nivel_culinario=NivelDificultad.PRINCIPIANTE,
    )
    perfil.ingredientes_evitados.append(tomate)

    estrategia = RestriccionIngredientesStrategy()

    assert estrategia.es_compatible(receta, perfil) is False


def test_ingredientes_acepta_receta_compatible():
    arroz = Ingrediente(
        id=2,
        nombre="Arroz",
        categoria_id=2,
    )

    tomate = Ingrediente(
        id=1,
        nombre="Tomate",
        categoria_id=1,
    )

    receta = crear_receta_con_ingrediente(arroz)

    perfil = PerfilAlimentario(
        cuenta_id=1,
        nivel_culinario=NivelDificultad.PRINCIPIANTE,
    )
    perfil.ingredientes_evitados.append(tomate)

    estrategia = RestriccionIngredientesStrategy()

    assert estrategia.es_compatible(receta, perfil) is True



def test_categorias_rechaza_receta_incompatible():
    lacteos = CategoriaAlimento(
        id=1,
        nombre="Lácteos",
    )

    queso = Ingrediente(
        id=1,
        nombre="Queso",
        categoria_id=lacteos.id,
    )

    receta = crear_receta_con_ingrediente(queso)

    perfil = PerfilAlimentario(
        cuenta_id=1,
        nivel_culinario=NivelDificultad.PRINCIPIANTE,
    )
    perfil.categorias_evitadas.append(lacteos)

    estrategia = RestriccionCategoriasStrategy()

    assert estrategia.es_compatible(receta, perfil) is False


def test_categorias_acepta_receta_compatible():
    lacteos = CategoriaAlimento(
        id=1,
        nombre="Lácteos",
    )

    arroz = Ingrediente(
        id=2,
        nombre="Arroz",
        categoria_id=2,
    )

    receta = crear_receta_con_ingrediente(arroz)

    perfil = PerfilAlimentario(
        cuenta_id=1,
        nivel_culinario=NivelDificultad.PRINCIPIANTE,
    )
    perfil.categorias_evitadas.append(lacteos)

    estrategia = RestriccionCategoriasStrategy()

    assert estrategia.es_compatible(receta, perfil) is True



def test_evaluador_acepta_receta_compatible():
    arroz = Ingrediente(
        id=1,
        nombre="Arroz",
        categoria_id=2,
    )

    receta = crear_receta_con_ingrediente(arroz)

    perfil = PerfilAlimentario(
        cuenta_id=1,
        nivel_culinario=NivelDificultad.PRINCIPIANTE,
    )

    perfil.alergias.append(
        Alergia(id=1, nombre="Leche")
    )

    perfil.ingredientes_evitados.append(
        Ingrediente(id=2, nombre="Tomate", categoria_id=3)
    )

    perfil.categorias_evitadas.append(
        CategoriaAlimento(id=1, nombre="Lácteos")
    )

    evaluador = crear_evaluador_restricciones()

    assert evaluador.es_compatible(receta, perfil) is True


def test_evaluador_rechaza_si_una_estrategia_falla():
    queso = Ingrediente(
        id=1,
        nombre="Queso",
        categoria_id=1,
    )

    receta = crear_receta_con_ingrediente(queso)

    perfil = PerfilAlimentario(
        cuenta_id=1,
        nivel_culinario=NivelDificultad.PRINCIPIANTE,
    )

    # No hay conflicto por alergias ni ingredientes evitados.
    perfil.alergias.append(
        Alergia(id=1, nombre="Huevo")
    )

    perfil.ingredientes_evitados.append(
        Ingrediente(id=2, nombre="Tomate", categoria_id=3)
    )

    # Pero la receta contiene queso, que pertenece a Lácteos.
    perfil.categorias_evitadas.append(
        CategoriaAlimento(id=1, nombre="Lácteos")
    )

    evaluador = crear_evaluador_restricciones()

    assert evaluador.es_compatible(receta, perfil) is False
