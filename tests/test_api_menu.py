from sqlalchemy import select

from app.models.categoria_alimento import CategoriaAlimento
from app.models.ingrediente import Ingrediente
from app.models.receta_ingrediente import RecetaIngrediente
from app.models.alternativa_ingrediente import AlternativaIngrediente
from app.models.cuenta import Cuenta
from app.services.preferencias_receta import PreferenciasRecetaService

from decimal import Decimal
from http import HTTPStatus

from sqlalchemy.orm import Session

from app.core.enums import TipoComida
from app.models.receta import Receta



from tests.test_recetas import (
    client,
    autenticar,
    crear_perfil,
    cargar_recetas,
)


def datos_menu(**cambios):
    datos = {
        "cantidad_dias": 1,
        "tipos_comida": [TipoComida.ALMUERZO.value],
        "comensales": 3,
        "tamano_porcion": "NORMAL",
    }
    datos.update(cambios)
    return datos


def test_generar_menu_con_cantidades_escaladas(client):
    test_client, engine = client

    ids = cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    # Solo modificamos los datos de esta prueba.
    with Session(engine) as db:
        receta = db.get(Receta, ids["receta_arroz"])
        assert receta is not None

        receta.porciones_base = 1
        db.commit()

    respuesta = test_client.post(
        "/menus/generar",
        headers=headers,
        json=datos_menu(),
    )

    assert respuesta.status_code == HTTPStatus.OK

    resultado = respuesta.json()

    assert resultado["estructura_completa"]
    assert len(resultado["comidas"]) == 1

    comida = resultado["comidas"][0]

    assert comida["dia"] == 1
    assert comida["tipo_comida"] == "ALMUERZO"
    assert comida["receta_id"] == ids["receta_arroz"]
    assert not comida["requiere_sustituciones"]

    assert len(comida["ingredientes"]) == 1

    ingrediente = comida["ingredientes"][0]

    assert Decimal(str(ingrediente["cantidad"])) == Decimal("450")
    assert ingrediente["unidad"] == "g"


def test_generar_menu_sin_autenticacion(client):
    test_client, _ = client

    respuesta = test_client.post(
        "/menus/generar",
        json=datos_menu(),
    )

    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED


def test_generar_menu_sin_perfil(client):
    test_client, _ = client

    headers = autenticar(test_client)

    respuesta = test_client.post(
        "/menus/generar",
        headers=headers,
        json=datos_menu(),
    )

    assert respuesta.status_code == HTTPStatus.CONFLICT


def test_generar_menu_rechaza_dias_invalidos(client):
    test_client, _ = client

    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    respuesta = test_client.post(
        "/menus/generar",
        headers=headers,
        json=datos_menu(cantidad_dias=0),
    )

    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_generar_menu_rechaza_tamano_no_implementado(client):
    test_client, _ = client

    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    respuesta = test_client.post(
        "/menus/generar",
        headers=headers,
        json=datos_menu(tamano_porcion="GRANDE"),
    )

    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_generar_menu_sin_porciones_base(client):
    test_client, engine = client

    cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    # Las recetas del fixture no tienen porciones_base.
    respuesta = test_client.post(
        "/menus/generar",
        headers=headers,
        json=datos_menu(),
    )

    assert respuesta.status_code == HTTPStatus.CONFLICT
    assert "porciones base" in respuesta.json()["detail"]


def test_generar_menu_sin_recetas_para_comida(client):
    test_client, engine = client

    cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    # El fixture no contiene recetas para CENA.
    respuesta = test_client.post(
        "/menus/generar",
        headers=headers,
        json=datos_menu(
            tipos_comida=[TipoComida.CENA.value],
        ),
    )

    assert respuesta.status_code == HTTPStatus.OK

    resultado = respuesta.json()

    assert not resultado["estructura_completa"]
    assert len(resultado["comidas"]) == 1

    comida = resultado["comidas"][0]

    assert comida["tipo_comida"] == "CENA"
    assert comida["receta_id"] is None
    assert comida["ingredientes"] == []

def test_generar_menu_con_sustitucion_pendiente(client):
    test_client, engine = client

    ids = cargar_recetas(engine)
    headers = autenticar(test_client)

    crear_perfil(
        test_client,
        headers,
        ingredientes_evitados_ids=[ids["leche"]],
    )

    # Incorporar una alternativa compatible para la receta
    # que contiene leche.
    with Session(engine) as db:
        receta = db.get(Receta, ids["receta_leche"])
        assert receta is not None
        receta.porciones_base = 1

        categoria = CategoriaAlimento(
            nombre="Bebidas vegetales"
        )
        db.add(categoria)
        db.flush()

        alternativa = Ingrediente(
            nombre="Bebida vegetal",
            categoria_id=categoria.id,
        )
        db.add(alternativa)
        db.flush()

        posicion = db.scalar(
            select(RecetaIngrediente).where(
                RecetaIngrediente.receta_id
                == ids["receta_leche"]
            )
        )

        assert posicion is not None

        db.add(
            AlternativaIngrediente(
                receta_ingrediente_id=posicion.id,
                ingrediente_alternativo_id=alternativa.id,
                cantidad=200,
                unidad="ml",
            )
        )

        db.commit()

    respuesta = test_client.post(
        "/menus/generar",
        headers=headers,
        json=datos_menu(
            tipos_comida=[TipoComida.DESAYUNO.value],
        ),
    )

    assert respuesta.status_code == HTTPStatus.OK

    resultado = respuesta.json()

    assert resultado["estructura_completa"]

    comida = resultado["comidas"][0]

    assert comida["receta_id"] == ids["receta_leche"]
    assert comida["requiere_sustituciones"]
    assert comida["ingredientes"] == []

def test_generador_respeta_exclusiones_personales(client):
    test_client, engine = client

    ids = cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    # Preparar una receta válida para el generador.
    with Session(engine) as db:
        cuenta_id = db.scalar(select(Cuenta.id))
        assert cuenta_id is not None

        receta = db.get(Receta, ids["receta_arroz"])
        assert receta is not None

        receta.porciones_base = 1
        db.commit()

    # Primero, la receta debe poder seleccionarse.
    respuesta_antes = test_client.post(
        "/menus/generar",
        headers=headers,
        json=datos_menu(),
    )

    assert respuesta_antes.status_code == HTTPStatus.OK
    assert (
        respuesta_antes.json()["comidas"][0]["receta_id"]
        == ids["receta_arroz"]
    )

    # El usuario excluye personalmente esa receta.
    with Session(engine) as db:
        preferencias = PreferenciasRecetaService(db)

        preferencias.agregar_exclusion(
            cuenta_id,
            ids["receta_arroz"],
        )

    # Generar nuevamente el mismo menú.
    respuesta_despues = test_client.post(
        "/menus/generar",
        headers=headers,
        json=datos_menu(),
    )

    assert respuesta_despues.status_code == HTTPStatus.OK

    resultado = respuesta_despues.json()

    # El fixture no tiene otra receta para ALMUERZO.
    assert not resultado["estructura_completa"]
    assert resultado["comidas"][0]["receta_id"] is None
    assert resultado["comidas"][0]["ingredientes"] == []