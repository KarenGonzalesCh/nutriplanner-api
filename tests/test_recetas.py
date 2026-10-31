
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

from app.core.enums import NivelDificultad, TipoComida
from app.models.alergia import Alergia
from app.models.categoria_alimento import CategoriaAlimento
from app.models.ingrediente import Ingrediente
from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente
from app.models.receta_tipo_comida import RecetaTipoComida


@pytest.fixture
def client():
    # Base de datos independiente para cada test
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    def get_db_test():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = get_db_test

    try:
        with TestClient(app) as test_client:
            yield test_client, engine
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(engine)
        engine.dispose()


def autenticar(client):
    registro = client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_recetas",
            "correo": "recetas@example.com",
            "password": "ClaveSegura123",
        },
    )
    assert registro.status_code == HTTPStatus.CREATED

    login = client.post(
        "/auth/token",
        data={
            "username": "recetas@example.com",
            "password": "ClaveSegura123",
        },
    )
    assert login.status_code == HTTPStatus.OK

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def crear_perfil(client, headers, **restricciones):
    datos = {
        "nivel_culinario": "PRINCIPIANTE",
        "alergias_ids": [],
        "ingredientes_evitados_ids": [],
        "categorias_evitadas_ids": [],
    }
    datos.update(restricciones)

    respuesta = client.post(
        "/perfil",
        headers=headers,
        json=datos,
    )
    assert respuesta.status_code == HTTPStatus.CREATED


def cargar_recetas(engine):
    # Datos de prueba: una receta con leche y otra con arroz
    with Session(engine) as session:
        lacteos = CategoriaAlimento(nombre="Lácteos")
        cereales = CategoriaAlimento(nombre="Cereales")
        alergia_leche = Alergia(nombre="Leche")

        session.add_all([lacteos, cereales, alergia_leche])
        session.flush()

        leche = Ingrediente(
            nombre="Leche",
            categoria_id=lacteos.id,
        )
        arroz = Ingrediente(
            nombre="Arroz",
            categoria_id=cereales.id,
        )
        leche.alergias.append(alergia_leche)

        session.add_all([leche, arroz])
        session.flush()

        receta_leche = Receta(
            nombre="Vaso de leche",
            pasos="Servir la leche.",
            tiempo_preparacion=2,
            dificultad=NivelDificultad.PRINCIPIANTE,
            info_nutricional=None,
            activa=True,
        )
        receta_leche.ingredientes.append(
            RecetaIngrediente(
                ingrediente_id=leche.id,
                cantidad=200,
                unidad="ml",
            )
        )
        receta_leche.tipos_comida.append(
            RecetaTipoComida(tipo_comida=TipoComida.DESAYUNO)
        )

        receta_arroz = Receta(
            nombre="Arroz hervido",
            pasos="Hervir el arroz en agua.",
            tiempo_preparacion=20,
            dificultad=NivelDificultad.PRINCIPIANTE,
            info_nutricional=None,
            activa=True,
        )
        receta_arroz.ingredientes.append(
            RecetaIngrediente(
                ingrediente_id=arroz.id,
                cantidad=150,
                unidad="g",
            )
        )
        receta_arroz.tipos_comida.append(
            RecetaTipoComida(tipo_comida=TipoComida.ALMUERZO)
        )

        receta_inactiva = Receta(
            nombre="Receta desactivada",
            pasos="No disponible.",
            tiempo_preparacion=10,
            dificultad=NivelDificultad.PRINCIPIANTE,
            info_nutricional=None,
            activa=False,
        )

        session.add_all([
            receta_leche,
            receta_arroz,
            receta_inactiva,
        ])
        session.flush()

        ids = {
            "leche": leche.id,
            "categoria_lacteos": lacteos.id,
            "alergia_leche": alergia_leche.id,
            "receta_leche": receta_leche.id,
            "receta_arroz": receta_arroz.id,
            "receta_inactiva": receta_inactiva.id,
        }

        session.commit()
        return ids


def test_listar_recetas_sin_autenticacion(client):
    test_client, _ = client

    respuesta = test_client.get("/recetas")

    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED


def test_listar_recetas_sin_perfil(client):
    test_client, _ = client
    headers = autenticar(test_client)

    respuesta = test_client.get("/recetas", headers=headers)

    assert respuesta.status_code == HTTPStatus.CONFLICT


def test_listar_catalogo_vacio(client):
    test_client, _ = client
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    respuesta = test_client.get("/recetas", headers=headers)

    assert respuesta.status_code == HTTPStatus.OK
    assert respuesta.json() == []


def test_listar_recetas_activas(client):
    test_client, engine = client
    ids = cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    respuesta = test_client.get("/recetas", headers=headers)

    assert respuesta.status_code == HTTPStatus.OK

    datos = respuesta.json()
    assert len(datos) == 2
    assert [r["nombre"] for r in datos] == [
        "Arroz hervido",
        "Vaso de leche",
    ]
    assert ids["receta_inactiva"] not in [r["id"] for r in datos]


def test_consultar_detalle_receta(client):
    test_client, engine = client
    ids = cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    respuesta = test_client.get(
        f"/recetas/{ids['receta_arroz']}",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.OK

    datos = respuesta.json()
    assert datos["nombre"] == "Arroz hervido"
    assert datos["tiempo_preparacion"] == 20
    assert datos["tipos_comida"] == ["ALMUERZO"]
    assert len(datos["ingredientes"]) == 1
    assert datos["ingredientes"][0]["nombre"] == "Arroz"
    assert datos["ingredientes"][0]["cantidad"] == 150


def test_receta_inexistente(client):
    test_client, _ = client
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    respuesta = test_client.get("/recetas/999", headers=headers)

    assert respuesta.status_code == HTTPStatus.NOT_FOUND


def test_receta_desactivada(client):
    test_client, engine = client
    ids = cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    respuesta = test_client.get(
        f"/recetas/{ids['receta_inactiva']}",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.NOT_FOUND


def test_filtrar_por_ingrediente_evitado(client):
    test_client, engine = client
    ids = cargar_recetas(engine)
    headers = autenticar(test_client)

    crear_perfil(
        test_client,
        headers,
        ingredientes_evitados_ids=[ids["leche"]],
    )

    respuesta = test_client.get("/recetas", headers=headers)

    assert respuesta.status_code == HTTPStatus.OK
    assert [r["nombre"] for r in respuesta.json()] == [
        "Arroz hervido"
    ]


def test_filtrar_por_categoria_evitada(client):
    test_client, engine = client
    ids = cargar_recetas(engine)
    headers = autenticar(test_client)

    crear_perfil(
        test_client,
        headers,
        categorias_evitadas_ids=[ids["categoria_lacteos"]],
    )

    respuesta = test_client.get("/recetas", headers=headers)

    assert respuesta.status_code == HTTPStatus.OK
    assert [r["nombre"] for r in respuesta.json()] == [
        "Arroz hervido"
    ]


def test_filtrar_por_alergia(client):
    test_client, engine = client
    ids = cargar_recetas(engine)
    headers = autenticar(test_client)

    crear_perfil(
        test_client,
        headers,
        alergias_ids=[ids["alergia_leche"]],
    )

    respuesta = test_client.get("/recetas", headers=headers)

    assert respuesta.status_code == HTTPStatus.OK
    assert [r["nombre"] for r in respuesta.json()] == [
        "Arroz hervido"
    ]


def test_detalle_receta_incompatible(client):
    test_client, engine = client
    ids = cargar_recetas(engine)
    headers = autenticar(test_client)

    crear_perfil(
        test_client,
        headers,
        ingredientes_evitados_ids=[ids["leche"]],
    )

    respuesta = test_client.get(
        f"/recetas/{ids['receta_leche']}",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.NOT_FOUND

def test_receta_excluida_sigue_visible_en_catalogo(client):
    test_client, engine = client
    ids = cargar_recetas(engine)

    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    receta_id = ids["receta_arroz"]

    # El usuario excluye la receta.
    respuesta = test_client.post(
        f"/recetas/{receta_id}/exclusion",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.NO_CONTENT

    # La receta debe seguir apareciendo en el catálogo.
    listado = test_client.get(
        "/recetas",
        headers=headers,
    )

    assert listado.status_code == HTTPStatus.OK

    recetas_ids = [
        receta["id"]
        for receta in listado.json()
    ]

    assert receta_id in recetas_ids
    assert ids["receta_leche"] in recetas_ids

    # La exclusión personal debe seguir registrada.
    exclusiones = test_client.get(
        "/recetas/excluidas",
        headers=headers,
    )

    assert exclusiones.status_code == HTTPStatus.OK
    assert receta_id in exclusiones.json()