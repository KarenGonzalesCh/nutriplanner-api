
import pytest

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cuenta import Cuenta
from app.repositories.receta import RecetaRepository
from app.core.enums import TipoComida


from app.services.generador_menu import (
    GeneradorMenuService,
    PerfilMenuRequeridoError,
)

from tests.test_recetas import (
    client,
    autenticar,
    crear_perfil,
    cargar_recetas,
)

def obtener_cuenta_id(db):
    cuenta_id = db.scalar(select(Cuenta.id))
    assert cuenta_id is not None
    return cuenta_id


def test_generar_menu_con_recetas_reales(client):
    test_client, engine = client

    cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    with Session(engine) as db:
        recetas = RecetaRepository(db).listar()
        assert recetas

        tipo_comida = recetas[0].tipos_comida[0].tipo_comida

        servicio = GeneradorMenuService(db)

        propuesta = servicio.generar(
            cuenta_id=obtener_cuenta_id(db),
            cantidad_dias=1,
            tipos_comida=[tipo_comida],
        )

        assert len(propuesta.comidas) == 1
        assert propuesta.comidas[0].receta_id is not None
        assert propuesta.completa


def test_generador_descarta_receta_incompatible(client):
    test_client, engine = client

    ids = cargar_recetas(engine)
    headers = autenticar(test_client)

    crear_perfil(
        test_client,
        headers,
        ingredientes_evitados_ids=[ids["leche"]],
    )

    with Session(engine) as db:
        receta_leche = RecetaRepository(db).obtener_por_id(
            ids["receta_leche"]
        )

        assert receta_leche is not None

        tipo_comida = receta_leche.tipos_comida[0].tipo_comida

        servicio = GeneradorMenuService(db)

        propuesta = servicio.generar(
            cuenta_id=obtener_cuenta_id(db),
            cantidad_dias=1,
            tipos_comida=[tipo_comida],
        )

        ids_generados = {
            comida.receta_id
            for comida in propuesta.comidas
        }

        assert ids["receta_leche"] not in ids_generados


def test_generador_exige_perfil(client):
    test_client, engine = client

    cargar_recetas(engine)
    autenticar(test_client)

    with Session(engine) as db:
        servicio = GeneradorMenuService(db)

        with pytest.raises(PerfilMenuRequeridoError):
            servicio.generar(
                cuenta_id=obtener_cuenta_id(db),
                cantidad_dias=1,
                tipos_comida=[TipoComida.ALMUERZO],
            )