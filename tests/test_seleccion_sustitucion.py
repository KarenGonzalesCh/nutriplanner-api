
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db import seed_catalogos, seed_recetas, seed_alternativas

from app.api.dependencies import obtener_cuenta_actual
from app.core.enums import NivelDificultad

from app.models.cuenta import Cuenta
from app.models.perfil_alimentario import PerfilAlimentario
from app.models.alergia import Alergia
from app.models.receta import Receta


@pytest.fixture
def entorno_prueba(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    SessionTest = sessionmaker(bind=engine)

    # Las precargas se ejecutan en SQLite, no en Supabase.
    for modulo in (
        seed_catalogos,
        seed_recetas,
        seed_alternativas,
    ):
        monkeypatch.setattr(
            modulo,
            "SessionLocal",
            SessionTest,
        )

    seed_catalogos.main()
    seed_recetas.main()
    seed_alternativas.main()

    with SessionTest() as db:
        cuenta = Cuenta(
            nombre_usuario="prueba_sustituciones",
            correo="sustituciones@example.com",
            password_hash="hash_de_prueba",
        )

        db.add(cuenta)
        db.flush()

        perfil = PerfilAlimentario(
            cuenta_id=cuenta.id,
            nivel_culinario=NivelDificultad.PRINCIPIANTE,
        )

        for nombre in ("Leche", "Frutos secos"):
            alergia = db.scalar(
                select(Alergia).where(
                    Alergia.nombre == nombre
                )
            )
            assert alergia is not None
            perfil.alergias.append(alergia)

        db.add(perfil)

        receta = db.scalar(
            select(Receta).where(
                Receta.nombre == "Avena con banana"
            )
        )

        assert receta is not None

        posicion = next(
            item
            for item in receta.ingredientes
            if item.ingrediente.nombre == "Leche"
        )

        alternativas = {
            item.ingrediente_alternativo.nombre: item.id
            for item in posicion.alternativas
        }

        cuenta_id = cuenta.id
        receta_id = receta.id
        posicion_id = posicion.id

        db.commit()

    def get_db_test():
        with SessionTest() as session:
            yield session

    def obtener_cuenta_test():
        with SessionTest() as session:
            return session.get(Cuenta, cuenta_id)

    app.dependency_overrides[get_db] = get_db_test
    app.dependency_overrides[
        obtener_cuenta_actual
    ] = obtener_cuenta_test

    try:
        with TestClient(app) as client:
            yield client, receta_id, posicion_id, alternativas
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(
            obtener_cuenta_actual, None
        )
        engine.dispose()


def test_guardar_cambiar_y_eliminar_sustitucion(
    entorno_prueba,
):
    client, receta_id, posicion_id, alternativas = entorno_prueba

    url_lista = f"/recetas/{receta_id}/sustituciones"
    url_guardar = f"{url_lista}/{posicion_id}"

    # Inicialmente no hay sustituciones guardadas.
    respuesta = client.get(url_lista)
    assert respuesta.status_code == 200
    assert respuesta.json() == []

    # Guardar leche de coco.
    respuesta = client.put(
        url_guardar,
        json={
            "alternativa_id": alternativas["Leche de coco"]
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Leche de coco"

    # Comprobar que se recupera desde la base.
    respuesta = client.get(url_lista)
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1
    assert respuesta.json()[0]["nombre"] == "Leche de coco"

    # Rechazar leche de almendras: alergia a frutos secos.
    respuesta = client.put(
        url_guardar,
        json={
            "alternativa_id": alternativas["Leche de almendras"]
        },
    )

    assert respuesta.status_code == 400

    # Cambiar la selección a bebida de avena.
    respuesta = client.put(
        url_guardar,
        json={
            "alternativa_id": alternativas["Bebida de avena"]
        },
    )

    assert respuesta.status_code == 200

    respuesta = client.get(url_lista)
    assert len(respuesta.json()) == 1
    assert respuesta.json()[0]["nombre"] == "Bebida de avena"

    # Eliminar la selección.
    respuesta = client.delete(url_guardar)
    assert respuesta.status_code == 204

    respuesta = client.get(url_lista)
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_sustituciones_requieren_autenticacion(entorno_prueba):
    client, receta_id, posicion_id, alternativas = entorno_prueba

    # Desactivar temporalmente el usuario simulado
    # para utilizar la autenticación real de FastAPI.
    autenticacion_simulada = app.dependency_overrides.pop(
        obtener_cuenta_actual
    )

    try:
        url_lista = f"/recetas/{receta_id}/sustituciones"
        url_guardar = f"{url_lista}/{posicion_id}"

        # No permitir consultar sin iniciar sesión.
        respuesta = client.get(url_lista)
        assert respuesta.status_code == 401

        # No permitir guardar sin iniciar sesión.
        respuesta = client.put(
            url_guardar,
            json={
                "alternativa_id": alternativas["Leche de coco"]
            },
        )
        assert respuesta.status_code == 401

        # No permitir eliminar sin iniciar sesión.
        respuesta = client.delete(url_guardar)
        assert respuesta.status_code == 401

    finally:
        # Restaurar la configuración original de la prueba.
        app.dependency_overrides[
            obtener_cuenta_actual
        ] = autenticacion_simulada


def test_sustituciones_independientes_por_usuario(entorno_prueba):
    client, receta_id, posicion_id, alternativas = entorno_prueba

    # Usar la autenticación real de FastAPI.
    autenticacion_simulada = app.dependency_overrides.pop(
        obtener_cuenta_actual
    )

    try:
        # Obtener los IDs de las alergias desde el catálogo.
        respuesta = client.get("/alergias")
        assert respuesta.status_code == 200

        alergias = {
            item["nombre"]: item["id"]
            for item in respuesta.json()
        }

        ids_alergias = [
            alergias["Leche"],
            alergias["Frutos secos"],
        ]

        def crear_usuario(numero):
            correo = f"sustitucion_usuario{numero}@example.com"
            password = "ClaveSegura123"

            registro = client.post(
                "/cuentas",
                json={
                    "nombre_usuario": f"sustitucion_usuario{numero}",
                    "correo": correo,
                    "password": password,
                },
            )
            assert registro.status_code == 201

            login = client.post(
                "/auth/token",
                data={
                    "username": correo,
                    "password": password,
                },
            )
            assert login.status_code == 200

            token = login.json()["access_token"]
            headers = {
                "Authorization": f"Bearer {token}"
            }

            perfil = client.post(
                "/perfil",
                headers=headers,
                json={
                    "nivel_culinario": "PRINCIPIANTE",
                    "alergias_ids": ids_alergias,
                    "ingredientes_evitados_ids": [],
                    "categorias_evitadas_ids": [],
                },
            )
            assert perfil.status_code == 201

            return headers

        usuario_1 = crear_usuario(1)
        usuario_2 = crear_usuario(2)

        url_lista = f"/recetas/{receta_id}/sustituciones"
        url_guardar = f"{url_lista}/{posicion_id}"

        # Usuario 1: guarda leche de coco.
        respuesta = client.put(
            url_guardar,
            headers=usuario_1,
            json={
                "alternativa_id": alternativas["Leche de coco"]
            },
        )
        assert respuesta.status_code == 200

        # Usuario 2: todavía no tiene ninguna selección.
        respuesta = client.get(
            url_lista,
            headers=usuario_2,
        )
        assert respuesta.status_code == 200
        assert respuesta.json() == []

        # Usuario 2: guarda bebida de avena.
        respuesta = client.put(
            url_guardar,
            headers=usuario_2,
            json={
                "alternativa_id": alternativas["Bebida de avena"]
            },
        )
        assert respuesta.status_code == 200

        # Cada usuario recupera su propia elección.
        respuesta_1 = client.get(
            url_lista,
            headers=usuario_1,
        )
        respuesta_2 = client.get(
            url_lista,
            headers=usuario_2,
        )

        assert respuesta_1.json()[0]["nombre"] == "Leche de coco"
        assert respuesta_2.json()[0]["nombre"] == "Bebida de avena"

        # Si el usuario 1 elimina su elección,
        # no debe eliminar la del usuario 2.
        respuesta = client.delete(
            url_guardar,
            headers=usuario_1,
        )
        assert respuesta.status_code == 204

        assert client.get(
            url_lista,
            headers=usuario_1,
        ).json() == []

        assert client.get(
            url_lista,
            headers=usuario_2,
        ).json()[0]["nombre"] == "Bebida de avena"

    finally:
        app.dependency_overrides[
            obtener_cuenta_actual
        ] = autenticacion_simulada

