import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db import seed_catalogos, seed_recetas, seed_alternativas
from app.models.alternativa_ingrediente import AlternativaIngrediente
from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente
from app.models.ingrediente import Ingrediente


@pytest.fixture
def db_test(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    SessionTest = sessionmaker(bind=engine)

    for modulo in (seed_catalogos, seed_recetas, seed_alternativas):
        monkeypatch.setattr(modulo, "SessionLocal", SessionTest)

    try:
        yield SessionTest
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_precarga_alternativas_es_idempotente(db_test):
    seed_catalogos.main()
    seed_recetas.main()

    # Ejecutar dos veces para comprobar que no duplica.
    seed_alternativas.main()
    seed_alternativas.main()

    with db_test() as db:
        alternativas = db.scalars(
            select(AlternativaIngrediente)
        ).all()

        assert len(alternativas) == 1

        alternativa = alternativas[0]

        posicion = db.get(
            RecetaIngrediente,
            alternativa.receta_ingrediente_id,
        )

        assert posicion is not None
        assert posicion.receta.nombre == "Ensalada de garbanzos"
        assert posicion.ingrediente.nombre == "Garbanzos"

        sustituto = db.get(
            Ingrediente,
            alternativa.ingrediente_alternativo_id,
        )

        assert sustituto.nombre == "Lentejas"
        assert alternativa.cantidad == 150
        assert alternativa.unidad == "g"
