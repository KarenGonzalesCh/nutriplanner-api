import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from types import SimpleNamespace

import app.models
from app.db.base import Base
from app.db import seed_catalogos, seed_recetas, seed_alternativas
from app.models.alternativa_ingrediente import AlternativaIngrediente
from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente
from app.models.ingrediente import Ingrediente
from app.models.alergia import Alergia
from app.services.compatibilidad_receta import EstadoCompatibilidad
from app.services.detalle_compatibilidad import preparar_detalle_compatibilidad


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

        assert len(alternativas) == 22

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

        recetas_con_leche = [
            "Avena con banana",
            "Avena con manzana",
            "Avena con almendras y banana",
            "Licuado de banana y avena",
            "Licuado de manzana y avena",
            "Licuado de frutillas y banana",
            "Porridge de avena y pera",
        ]

        for nombre_receta in recetas_con_leche:
            posicion_leche = db.scalar(
                select(RecetaIngrediente)
                .join(Receta)
                .join(
                    Ingrediente,
                    RecetaIngrediente.ingrediente_id == Ingrediente.id,
                )
                .where(
                    Receta.nombre == nombre_receta,
                    Ingrediente.nombre == "Leche",
                )
            )

            assert posicion_leche is not None

            sustitutos = {
                alternativa.ingrediente_alternativo.nombre
                for alternativa in posicion_leche.alternativas
            }

            assert sustitutos == {
                "Leche de coco",
                "Leche de almendras",
                "Bebida de avena",
            }

def test_avena_con_banana_es_adaptable(db_test):
    seed_catalogos.main()
    seed_recetas.main()
    seed_alternativas.main()

    with db_test() as db:
        receta = db.scalar(
            select(Receta).where(
                Receta.nombre == "Avena con banana"
            )
        )

        alergia_leche = db.scalar(
            select(Alergia).where(
                Alergia.nombre == "Leche"
            )
        )

        alergia_frutos_secos = db.scalar(
            select(Alergia).where(
                Alergia.nombre == "Frutos secos"
            )
        )

        perfil = SimpleNamespace(
            alergias=[alergia_leche, alergia_frutos_secos],
            ingredientes_evitados=[],
            categorias_evitadas=[],
        )

        detalle = preparar_detalle_compatibilidad(
            receta, perfil
        )

        assert detalle.estado_compatibilidad == (
            EstadoCompatibilidad.ADAPTABLE
        )

        restringido = detalle.ingredientes_restringidos[0]

        assert restringido.nombre == "Leche"

        alternativas = {
            alternativa.nombre
            for alternativa in restringido.alternativas_validas
        }

        assert alternativas == {
            "Leche de coco",
            "Bebida de avena",
        }