
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db import seed_catalogos, seed_recetas
from app.models.receta import Receta


@pytest.fixture
def db_test(monkeypatch):
    # Base SQLite temporal para cada test
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    SessionTest = sessionmaker(bind=engine)

    # Ambas precargas usarán la base temporal
    monkeypatch.setattr(
        seed_catalogos, "SessionLocal", SessionTest
    )
    monkeypatch.setattr(
        seed_recetas, "SessionLocal", SessionTest
    )

    try:
        yield SessionTest
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def verificar_cantidades(db_test):
    with db_test() as db:
        recetas = db.scalars(select(Receta)).all()

        assert len(recetas) == 5

        assert sum(
            len(receta.ingredientes) for receta in recetas
        ) == 15

        assert sum(
            len(receta.tipos_comida) for receta in recetas
        ) == 10


def test_precarga_inicial_recetas(db_test):
    seed_catalogos.main()
    seed_recetas.main()

    verificar_cantidades(db_test)


def test_precarga_recetas_no_duplica(db_test):
    seed_catalogos.main()

    seed_recetas.main()
    seed_recetas.main()

    verificar_cantidades(db_test)
