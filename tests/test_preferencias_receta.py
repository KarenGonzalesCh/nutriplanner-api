
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.enums import NivelDificultad
from app.models.receta import Receta


@pytest.fixture
def client():
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


def autenticar(client, numero):
    correo = f"usuario{numero}@example.com"

    registro = client.post(
        "/cuentas",
        json={
            "nombre_usuario": f"usuario{numero}",
            "correo": correo,
            "password": "ClaveSegura123",
        },
    )
    assert registro.status_code == HTTPStatus.CREATED

    login = client.post(
        "/auth/token",
        data={
            "username": correo,
            "password": "ClaveSegura123",
        },
    )
    assert login.status_code == HTTPStatus.OK

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def crear_receta(engine):
    with Session(engine) as session:
        receta = Receta(
            nombre="Arroz hervido",
            pasos="Hervir el arroz.",
            tiempo_preparacion=20,
            dificultad=NivelDificultad.PRINCIPIANTE,
            info_nutricional=None,
            activa=True,
        )
        session.add(receta)
        session.commit()
        return receta.id


def test_favoritas_sin_autenticacion(client):
    test_client, _ = client

    respuesta = test_client.get("/recetas/favoritas")

    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED


def test_agregar_y_listar_favorita(client):
    test_client, engine = client
    receta_id = crear_receta(engine)
    headers = autenticar(test_client, 1)

    respuesta = test_client.post(
        f"/recetas/{receta_id}/favorita",
        headers=headers,
    )
    assert respuesta.status_code == HTTPStatus.NO_CONTENT

    listado = test_client.get(
        "/recetas/favoritas",
        headers=headers,
    )
    assert listado.status_code == HTTPStatus.OK
    assert listado.json() == [receta_id]


def test_agregar_favorita_duplicada(client):
    test_client, engine = client
    receta_id = crear_receta(engine)
    headers = autenticar(test_client, 1)

    for _ in range(2):
        respuesta = test_client.post(
            f"/recetas/{receta_id}/favorita",
            headers=headers,
        )
        assert respuesta.status_code == HTTPStatus.NO_CONTENT

    listado = test_client.get(
        "/recetas/favoritas",
        headers=headers,
    )
    assert listado.json() == [receta_id]


def test_quitar_favorita(client):
    test_client, engine = client
    receta_id = crear_receta(engine)
    headers = autenticar(test_client, 1)

    test_client.post(
        f"/recetas/{receta_id}/favorita",
        headers=headers,
    )

    respuesta = test_client.delete(
        f"/recetas/{receta_id}/favorita",
        headers=headers,
    )
    assert respuesta.status_code == HTTPStatus.NO_CONTENT

    listado = test_client.get(
        "/recetas/favoritas",
        headers=headers,
    )
    assert listado.json() == []


def test_favorita_receta_inexistente(client):
    test_client, _ = client
    headers = autenticar(test_client, 1)

    respuesta = test_client.post(
        "/recetas/999/favorita",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.NOT_FOUND


def test_agregar_y_listar_exclusion(client):
    test_client, engine = client
    receta_id = crear_receta(engine)
    headers = autenticar(test_client, 1)

    respuesta = test_client.post(
        f"/recetas/{receta_id}/exclusion",
        headers=headers,
    )
    assert respuesta.status_code == HTTPStatus.NO_CONTENT

    listado = test_client.get(
        "/recetas/excluidas",
        headers=headers,
    )
    assert listado.status_code == HTTPStatus.OK
    assert listado.json() == [receta_id]


def test_quitar_exclusion(client):
    test_client, engine = client
    receta_id = crear_receta(engine)
    headers = autenticar(test_client, 1)

    test_client.post(
        f"/recetas/{receta_id}/exclusion",
        headers=headers,
    )

    respuesta = test_client.delete(
        f"/recetas/{receta_id}/exclusion",
        headers=headers,
    )
    assert respuesta.status_code == HTTPStatus.NO_CONTENT

    listado = test_client.get(
        "/recetas/excluidas",
        headers=headers,
    )
    assert listado.json() == []


def test_favorita_y_excluida_simultaneamente(client):
    test_client, engine = client
    receta_id = crear_receta(engine)
    headers = autenticar(test_client, 1)

    test_client.post(
        f"/recetas/{receta_id}/favorita",
        headers=headers,
    )
    test_client.post(
        f"/recetas/{receta_id}/exclusion",
        headers=headers,
    )

    favoritas = test_client.get(
        "/recetas/favoritas",
        headers=headers,
    )
    excluidas = test_client.get(
        "/recetas/excluidas",
        headers=headers,
    )

    assert favoritas.json() == [receta_id]
    assert excluidas.json() == [receta_id]


def test_preferencias_independientes_por_usuario(client):
    test_client, engine = client
    receta_id = crear_receta(engine)

    headers_1 = autenticar(test_client, 1)
    headers_2 = autenticar(test_client, 2)

    test_client.post(
        f"/recetas/{receta_id}/favorita",
        headers=headers_1,
    )
    test_client.post(
        f"/recetas/{receta_id}/exclusion",
        headers=headers_2,
    )

    favoritas_1 = test_client.get(
        "/recetas/favoritas",
        headers=headers_1,
    )
    favoritas_2 = test_client.get(
        "/recetas/favoritas",
        headers=headers_2,
    )

    excluidas_1 = test_client.get(
        "/recetas/excluidas",
        headers=headers_1,
    )
    excluidas_2 = test_client.get(
        "/recetas/excluidas",
        headers=headers_2,
    )

    assert favoritas_1.json() == [receta_id]
    assert favoritas_2.json() == []
    assert excluidas_1.json() == []
    assert excluidas_2.json() == [receta_id]
