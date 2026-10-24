
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.alergia import Alergia


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


def test_listar_alergias_catalogo_vacio(client):
    test_client, _ = client

    respuesta = test_client.get("/alergias")

    assert respuesta.status_code == HTTPStatus.OK
    assert respuesta.json() == []


def test_listar_alergias_ordenadas(client):
    test_client, engine = client

    # Cargar alergias en la base temporal
    with Session(engine) as session:
        session.add_all([
            Alergia(nombre="Maní"),
            Alergia(nombre="Huevo"),
            Alergia(nombre="Leche"),
        ])
        session.commit()

    respuesta = test_client.get("/alergias")

    assert respuesta.status_code == HTTPStatus.OK

    datos = respuesta.json()

    assert len(datos) == 3
    assert [a["nombre"] for a in datos] == [
        "Huevo",
        "Leche",
        "Maní",
    ]
    assert all(isinstance(a["id"], int) for a in datos)
