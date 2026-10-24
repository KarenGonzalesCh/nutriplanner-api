
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.categoria_alimento import CategoriaAlimento


@pytest.fixture
def client():
    # Crear una base SQLite temporal para cada test
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


def test_listar_categorias_catalogo_vacio(client):
    test_client, _ = client

    respuesta = test_client.get("/categorias-alimento")

    assert respuesta.status_code == HTTPStatus.OK
    assert respuesta.json() == []


def test_listar_categorias_ordenadas(client):
    test_client, engine = client

    # Agregar categorías a la base de pruebas
    with Session(engine) as session:
        session.add_all([
            CategoriaAlimento(nombre="Verduras"),
            CategoriaAlimento(nombre="Cereales"),
            CategoriaAlimento(nombre="Frutas"),
        ])
        session.commit()

    respuesta = test_client.get("/categorias-alimento")

    assert respuesta.status_code == HTTPStatus.OK

    datos = respuesta.json()

    assert len(datos) == 3
    assert [categoria["nombre"] for categoria in datos] == [
        "Cereales",
        "Frutas",
        "Verduras",
    ]
    assert all(isinstance(categoria["id"], int) for categoria in datos)
