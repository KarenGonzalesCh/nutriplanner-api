from http import HTTPStatus

from sqlalchemy import select
from sqlalchemy.orm import Session

from tests.test_recetas import (
    client,
    autenticar,
    crear_perfil,
    cargar_recetas,
)

from app.models.categoria_alimento import CategoriaAlimento
from app.models.ingrediente import Ingrediente
from app.models.receta_ingrediente import RecetaIngrediente
from app.models.alternativa_ingrediente import AlternativaIngrediente


def test_endpoint_compatibilidad_tres_estados(client):
    test_client, engine = client

    # Crear recetas e ingredientes de prueba.
    ids = cargar_recetas(engine)

    # Autenticar usuario y configurar restricción de leche.
    headers = autenticar(test_client)

    crear_perfil(
        test_client,
        headers,
        ingredientes_evitados_ids=[ids["leche"]],
    )

    # 1. Receta compatible: arroz.
    respuesta = test_client.get(
        f"/recetas/{ids['receta_arroz']}/compatibilidad",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.OK
    assert respuesta.json()["estado_compatibilidad"] == "COMPATIBLE"
    assert respuesta.json()["ingredientes_restringidos"] == []

    # 2. Receta incompatible: leche sin alternativas.
    respuesta = test_client.get(
        f"/recetas/{ids['receta_leche']}/compatibilidad",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.OK
    assert respuesta.json()["estado_compatibilidad"] == "INCOMPATIBLE"

    # Agregar una alternativa específica a la receta con leche.
    with Session(engine) as db:
        categoria = CategoriaAlimento(nombre="Bebidas vegetales")
        db.add(categoria)
        db.flush()

        sustituto = Ingrediente(
            nombre="Bebida vegetal",
            categoria_id=categoria.id,
        )
        db.add(sustituto)
        db.flush()

        posicion = db.scalar(
            select(RecetaIngrediente).where(
                RecetaIngrediente.receta_id == ids["receta_leche"]
            )
        )
        assert posicion is not None

        db.add(
            AlternativaIngrediente(
                receta_ingrediente_id=posicion.id,
                ingrediente_alternativo_id=sustituto.id,
                cantidad=200,
                unidad="ml",
            )
        )
        db.commit()

    # 3. La receta ahora debe ser adaptable.
    respuesta = test_client.get(
        f"/recetas/{ids['receta_leche']}/compatibilidad",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.OK

    datos = respuesta.json()

    assert datos["estado_compatibilidad"] == "ADAPTABLE"
    assert len(datos["ingredientes_restringidos"]) == 1

    alternativas = datos["ingredientes_restringidos"][0]["alternativas_validas"]

    assert len(alternativas) == 1
    assert alternativas[0]["nombre"] == "Bebida vegetal"
    assert alternativas[0]["cantidad"] == 200
    assert alternativas[0]["unidad"] == "ml"


def test_compatibilidad_sin_autenticacion(client):
    test_client, _ = client

    respuesta = test_client.get("/recetas/1/compatibilidad")

    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED


def test_compatibilidad_sin_perfil(client):
    test_client, engine = client
    ids = cargar_recetas(engine)
    headers = autenticar(test_client)

    respuesta = test_client.get(
        f"/recetas/{ids['receta_leche']}/compatibilidad",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.CONFLICT


def test_compatibilidad_receta_inexistente(client):
    test_client, _ = client
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    respuesta = test_client.get(
        "/recetas/999999/compatibilidad",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.NOT_FOUND


def test_compatibilidad_receta_inactiva(client):
    test_client, engine = client
    ids = cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    respuesta = test_client.get(
        f"/recetas/{ids['receta_inactiva']}/compatibilidad",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.NOT_FOUND
