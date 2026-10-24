
import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db import seed_catalogos
from app.models.alergia import Alergia
from app.models.categoria_alimento import CategoriaAlimento
from app.models.ingrediente import Ingrediente


@pytest.fixture
def db_test(monkeypatch):
    # Base temporal, independiente de la base de desarrollo
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    SessionTest = sessionmaker(bind=engine)

    # Hacer que el script use la base de pruebas
    monkeypatch.setattr(
        seed_catalogos,
        "SessionLocal",
        SessionTest,
    )

    try:
        yield SessionTest
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_precarga_inicial(db_test):
    seed_catalogos.main()

    with db_test() as db:
        cantidad_categorias = db.scalar(
            select(func.count()).select_from(CategoriaAlimento)
        )

        cantidad_alergias = db.scalar(
            select(func.count()).select_from(Alergia)
        )

        cantidad_ingredientes = db.scalar(
            select(func.count()).select_from(Ingrediente)
        )

        assert cantidad_categorias == 10
        assert cantidad_alergias == 9
        assert cantidad_ingredientes == 23

        queso = db.scalar(
            select(Ingrediente).where(
                Ingrediente.nombre == "Queso"
            )
        )

        assert [alergia.nombre for alergia in queso.alergias] == [
            "Leche"
        ]


def test_precarga_no_duplica_datos(db_test):
    # Ejecutar la precarga dos veces
    seed_catalogos.main()
    seed_catalogos.main()

    with db_test() as db:
        categorias = db.scalars(
            select(CategoriaAlimento)
        ).all()

        alergias = db.scalars(
            select(Alergia)
        ).all()

        ingredientes = db.scalars(
            select(Ingrediente)
        ).all()

        assert len(categorias) == 10
        assert len(alergias) == 9
        assert len(ingredientes) == 23

        cantidad_relaciones = sum(
            len(ingrediente.alergias)
            for ingrediente in ingredientes
        )

        assert cantidad_relaciones == 11
