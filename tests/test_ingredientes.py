
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
from app.models.ingrediente import Ingrediente


@pytest.fixture
def client():
    # Base SQLite en memoria, independiente para cada test
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


def test_listar_ingredientes_catalogo_vacio(client):
    test_client, _ = client

    respuesta = test_client.get("/ingredientes")

    assert respuesta.status_code == HTTPStatus.OK
    assert respuesta.json() == []


def test_listar_ingredientes_ordenados(client):
    test_client, engine = client

    with Session(engine) as session:
        # Primero creamos la categoría
        categoria = CategoriaAlimento(nombre="Alimentos básicos")
        session.add(categoria)
        session.flush()

        # Después creamos los ingredientes asociados
        session.add_all([
            Ingrediente(nombre="Leche", categoria_id=categoria.id),
            Ingrediente(nombre="Arroz", categoria_id=categoria.id),
            Ingrediente(nombre="Huevo", categoria_id=categoria.id),
        ])
        session.commit()

        categoria_id = categoria.id

    respuesta = test_client.get("/ingredientes")

    assert respuesta.status_code == HTTPStatus.OK

    datos = respuesta.json()

    assert len(datos) == 3

    assert [ingrediente["nombre"] for ingrediente in datos] == [
        "Arroz",
        "Huevo",
        "Leche",
    ]

    assert all(isinstance(ingrediente["id"], int) for ingrediente in datos)

    assert all(
        ingrediente["categoria_id"] == categoria_id
        for ingrediente in datos
    )
