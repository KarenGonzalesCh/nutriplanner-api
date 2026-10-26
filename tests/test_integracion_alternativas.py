from app.services.detalle_compatibilidad import preparar_detalle_compatibilidad
from types import SimpleNamespace

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.core.enums import NivelDificultad
from app.models.alternativa_ingrediente import AlternativaIngrediente
from app.models.categoria_alimento import CategoriaAlimento
from app.models.ingrediente import Ingrediente
from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente
from app.services.compatibilidad_receta import (
    EstadoCompatibilidad,
    evaluar_compatibilidad_receta,
)


def test_alternativa_es_especifica_de_cada_receta():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    try:
        with Session(engine) as db:
            lacteos = CategoriaAlimento(nombre="Lácteos")
            vegetales = CategoriaAlimento(nombre="Vegetales")
            db.add_all([lacteos, vegetales])
            db.flush()

            leche = Ingrediente(
                nombre="Leche", categoria_id=lacteos.id
            )
            bebida = Ingrediente(
                nombre="Bebida vegetal", categoria_id=vegetales.id
            )
            db.add_all([leche, bebida])
            db.flush()

            def crear_receta(nombre):
                receta = Receta(
                    nombre=nombre,
                    pasos="Preparar y servir.",
                    tiempo_preparacion=10,
                    dificultad=NivelDificultad.PRINCIPIANTE,
                    activa=True,
                )
                receta.ingredientes.append(
                    RecetaIngrediente(
                        ingrediente=leche,
                        cantidad=200,
                        unidad="ml",
                    )
                )
                return receta

            panqueques = crear_receta("Panqueques")
            vaso_leche = crear_receta("Vaso de leche")

            db.add_all([panqueques, vaso_leche])
            db.flush()

            db.add(
                AlternativaIngrediente(
                    receta_ingrediente=panqueques.ingredientes[0],
                    ingrediente_alternativo=bebida,
                    cantidad=200,
                    unidad="ml",
                )
            )
            db.commit()

            db.expire_all()

            recetas = db.scalars(select(Receta)).all()
            por_nombre = {r.nombre: r for r in recetas}

            panqueques = por_nombre["Panqueques"]
            vaso_leche = por_nombre["Vaso de leche"]

            perfil = SimpleNamespace(
                alergias=[],
                ingredientes_evitados=[leche],
                categorias_evitadas=[],
            )

            assert len(panqueques.ingredientes[0].alternativas) == 1
            assert len(vaso_leche.ingredientes[0].alternativas) == 0

            assert evaluar_compatibilidad_receta(
                panqueques, perfil
            ) == EstadoCompatibilidad.ADAPTABLE

            assert evaluar_compatibilidad_receta(
                vaso_leche, perfil
            ) == EstadoCompatibilidad.INCOMPATIBLE


            # Verificar la respuesta detallada para el frontend.
            detalle_panqueques = preparar_detalle_compatibilidad(
                panqueques, perfil
            )

            assert detalle_panqueques.receta_id == panqueques.id
            assert detalle_panqueques.estado_compatibilidad == (
                EstadoCompatibilidad.ADAPTABLE
            )

            restringidos = detalle_panqueques.ingredientes_restringidos
            assert len(restringidos) == 1
            assert restringidos[0].nombre == "Leche"
            assert len(restringidos[0].alternativas_validas) == 1

            alternativa = restringidos[0].alternativas_validas[0]
            assert alternativa.nombre == "Bebida vegetal"
            assert alternativa.ingrediente_id == bebida.id
            assert alternativa.cantidad == 200
            assert alternativa.unidad == "ml"

            # La otra receta sigue siendo incompatible.
            detalle_vaso = preparar_detalle_compatibilidad(
                vaso_leche, perfil
            )

            assert detalle_vaso.estado_compatibilidad == (
                EstadoCompatibilidad.INCOMPATIBLE
            )
            assert len(detalle_vaso.ingredientes_restringidos) == 1
            assert (
                detalle_vaso.ingredientes_restringidos[0].alternativas_validas
                == []
            )

    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
