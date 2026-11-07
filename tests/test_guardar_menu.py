from decimal import Decimal

import pytest

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu import Menu, MenuComida
from app.models.cuenta import Cuenta
from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente
from app.models.ingrediente import Ingrediente
from app.models.categoria_alimento import CategoriaAlimento
from app.models.alternativa_ingrediente import AlternativaIngrediente

from app.schemas.menu import GuardarMenuRequest
from app.services.guardar_menu import (
    GuardarMenuService,
    MenuInvalidoError,
)

from tests.test_recetas import (
    client,
    autenticar,
    crear_perfil,
    cargar_recetas,
)


def test_guardar_menu_con_sustituciones_distintas(client):
    test_client, engine = client

    # Preparar recetas y un usuario de prueba.
    ids = cargar_recetas(engine)
    headers = autenticar(test_client)

    crear_perfil(
        test_client,
        headers,
        ingredientes_evitados_ids=[ids["leche"]],
    )

    with Session(engine) as db:
        cuenta_id = db.scalar(select(Cuenta.id))

        receta = db.get(Receta, ids["receta_leche"])
        assert receta is not None
        receta.porciones_base = 1

        # Crear alternativas dentro de la base temporal.
        categoria = CategoriaAlimento(
            nombre="Bebidas vegetales"
        )
        db.add(categoria)
        db.flush()

        coco = Ingrediente(
            nombre="Leche de coco",
            categoria_id=categoria.id,
        )

        avena = Ingrediente(
            nombre="Bebida de avena",
            categoria_id=categoria.id,
        )

        db.add_all([coco, avena])
        db.flush()

        posicion = db.scalar(
            select(RecetaIngrediente).where(
                RecetaIngrediente.receta_id
                == ids["receta_leche"]
            )
        )

        assert posicion is not None

        alternativa_coco = AlternativaIngrediente(
            receta_ingrediente_id=posicion.id,
            ingrediente_alternativo_id=coco.id,
            cantidad=200,
            unidad="ml",
        )

        alternativa_avena = AlternativaIngrediente(
            receta_ingrediente_id=posicion.id,
            ingrediente_alternativo_id=avena.id,
            cantidad=200,
            unidad="ml",
        )

        db.add_all([
            alternativa_coco,
            alternativa_avena,
        ])
        db.flush()

        posicion_id = posicion.id
        coco_id = alternativa_coco.id
        avena_id = alternativa_avena.id

        db.commit()

    assert cuenta_id is not None

    # La misma receta aparece en dos días diferentes.
    datos = GuardarMenuRequest(
        nombre="Menú de prueba",
        cantidad_dias=2,
        comensales=2,
        comidas=[
            {
                "dia": 1,
                "tipo_comida": "DESAYUNO",
                "receta_id": ids["receta_leche"],
                "sustituciones": [
                    {
                        "receta_ingrediente_id": posicion_id,
                        "alternativa_id": coco_id,
                    }
                ],
            },
            {
                "dia": 2,
                "tipo_comida": "DESAYUNO",
                "receta_id": ids["receta_leche"],
                "sustituciones": [
                    {
                        "receta_ingrediente_id": posicion_id,
                        "alternativa_id": avena_id,
                    }
                ],
            },
        ],
    )

    # Guardar usando el servicio real.
    with Session(engine) as db:
        servicio = GuardarMenuService(db)

        menu = servicio.guardar(
            cuenta_id=cuenta_id,
            datos=datos,
        )

        menu_id = menu.id

    # Abrir otra sesión para verificar la persistencia.
    with Session(engine) as db:
        menu = db.get(Menu, menu_id)

        assert menu is not None
        assert menu.nombre == "Menú de prueba"
        assert menu.cantidad_dias == 2
        assert menu.comensales == 2

        comidas = db.scalars(
            select(MenuComida)
            .where(MenuComida.menu_id == menu_id)
            .order_by(MenuComida.dia)
        ).all()

        assert len(comidas) == 2

        ingrediente_lunes = (
            comidas[0].instantanea["ingredientes"][0]
        )

        ingrediente_martes = (
            comidas[1].instantanea["ingredientes"][0]
        )

        assert ingrediente_lunes["nombre"] == "Leche de coco"
        assert ingrediente_martes["nombre"] == "Bebida de avena"

        # Dos comensales: 200 ml se convierten en 400 ml.
        assert Decimal(ingrediente_lunes["cantidad"]) == Decimal("400")
        assert Decimal(ingrediente_martes["cantidad"]) == Decimal("400")

        # Cada comida conserva su propia elección.
        assert (
            ingrediente_lunes["sustitucion"]["alternativa_id"]
            == coco_id
        )

        assert (
            ingrediente_martes["sustitucion"]["alternativa_id"]
            == avena_id
        )


def test_no_guarda_menu_con_sustitucion_pendiente(client):
    test_client, engine = client

    ids = cargar_recetas(engine)
    headers = autenticar(test_client)

    crear_perfil(
        test_client,
        headers,
        ingredientes_evitados_ids=[ids["leche"]],
    )

    with Session(engine) as db:
        cuenta_id = db.scalar(select(Cuenta.id))
        assert cuenta_id is not None

        for receta_id in (
            ids["receta_arroz"],
            ids["receta_leche"],
        ):
            receta = db.get(Receta, receta_id)
            assert receta is not None
            receta.porciones_base = 1

        db.commit()

    datos = GuardarMenuRequest(
        nombre="Menú inválido",
        cantidad_dias=2,
        comensales=1,
        comidas=[
            {
                "dia": 1,
                "tipo_comida": "ALMUERZO",
                "receta_id": ids["receta_arroz"],
                "sustituciones": [],
            },
            {
                "dia": 2,
                "tipo_comida": "DESAYUNO",
                "receta_id": ids["receta_leche"],
                "sustituciones": [],
            },
        ],
    )

    with Session(engine) as db:
        servicio = GuardarMenuService(db)

        with pytest.raises(
            MenuInvalidoError,
            match="Falta confirmar",
        ):
            servicio.guardar(
                cuenta_id=cuenta_id,
                datos=datos,
            )

    # Verificar que no se guardó parcialmente.
    with Session(engine) as db:
        assert db.scalar(select(Menu.id)) is None
        assert db.scalar(select(MenuComida.id)) is None



def test_no_guarda_menu_con_dia_vacio(client):
    test_client, engine = client

    ids = cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    with Session(engine) as db:
        cuenta_id = db.scalar(select(Cuenta.id))
        assert cuenta_id is not None

        # El menú solicita 2 días, pero solo tiene
        # una comida asignada al día 1.
        datos = GuardarMenuRequest(
            nombre="Menú incompleto",
            cantidad_dias=2,
            comensales=1,
            comidas=[
                {
                    "dia": 1,
                    "tipo_comida": "ALMUERZO",
                    "receta_id": ids["receta_arroz"],
                    "sustituciones": [],
                }
            ],
        )

        servicio = GuardarMenuService(db)

        with pytest.raises(
            MenuInvalidoError,
            match="todos los días",
        ):
            servicio.guardar(
                cuenta_id=cuenta_id,
                datos=datos,
            )

    # El menú rechazado no debe persistirse.
    with Session(engine) as db:
        assert db.scalar(select(Menu.id)) is None
        assert db.scalar(select(MenuComida.id)) is None
