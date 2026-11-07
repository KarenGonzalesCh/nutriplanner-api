
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.cuenta import Cuenta


@pytest.fixture
def entorno_verificacion(monkeypatch):
    # Activamos la verificación solo durante cada prueba.
    monkeypatch.setattr(
        settings, "email_verification_enabled", True
    )
    monkeypatch.setattr(
        settings, "resend_api_key", "clave-ficticia"
    )
    monkeypatch.setattr(
        settings, "email_from", "pruebas@example.com"
    )
    monkeypatch.setattr(
        settings, "frontend_url", "http://localhost:8080"
    )

    # No enviamos correos reales: guardamos los enlaces.
    enlaces_enviados = []

    def correo_simulado(destinatario, enlace):
        enlaces_enviados.append(enlace)

    monkeypatch.setattr(
        "app.services.verificacion_correo.enviar_correo",
        correo_simulado,
    )

    # Base de datos SQLite independiente de la real.
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
        with TestClient(app) as client:
            yield client, engine, enlaces_enviados
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(engine)
        engine.dispose()


def registrar(client, correo="nuevo@example.com"):
    return client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_nuevo",
            "correo": correo,
            "password": "ClaveSegura123",
        },
    )


def login(client, correo="nuevo@example.com"):
    return client.post(
        "/auth/token",
        data={
            "username": correo,
            "password": "ClaveSegura123",
        },
    )


def extraer_token(enlace):
    parametros = parse_qs(urlsplit(enlace).query)
    return parametros["token"][0]


def test_login_bloqueado_hasta_confirmar(entorno_verificacion):
    client, engine, enlaces = entorno_verificacion

    respuesta = registrar(client)

    assert respuesta.status_code == 201
    assert respuesta.json()["correo_verificado"] is False
    assert len(enlaces) == 1

    # Antes de confirmar, el acceso debe estar bloqueado.
    respuesta_login = login(client)
    assert respuesta_login.status_code == 403

    # Simulamos que el usuario abre el enlace recibido.
    token = extraer_token(enlaces[0])

    confirmacion = client.post(
        "/auth/verificar-correo",
        json={"token": token},
    )

    assert confirmacion.status_code == 200

    # Ahora sí puede ingresar.
    respuesta_login = login(client)

    assert respuesta_login.status_code == 200
    assert "access_token" in respuesta_login.json()

    # Verificamos que la base registró el cambio.
    with Session(engine) as session:
        cuenta = session.scalar(
            select(Cuenta).where(
                Cuenta.correo == "nuevo@example.com"
            )
        )
        assert cuenta.correo_verificado is True
        assert cuenta.verificacion_token_hash is None


def test_token_no_puede_utilizarse_dos_veces(
    entorno_verificacion,
):
    client, _, enlaces = entorno_verificacion

    assert registrar(client).status_code == 201

    token = extraer_token(enlaces[0])

    primera = client.post(
        "/auth/verificar-correo",
        json={"token": token},
    )
    assert primera.status_code == 200

    segunda = client.post(
        "/auth/verificar-correo",
        json={"token": token},
    )
    assert segunda.status_code == 400


def test_token_vencido_no_confirma(entorno_verificacion):
    client, engine, enlaces = entorno_verificacion

    assert registrar(client).status_code == 201

    # Simulamos que el enlace ya venció.
    with Session(engine) as session:
        cuenta = session.scalar(
            select(Cuenta).where(
                Cuenta.correo == "nuevo@example.com"
            )
        )
        cuenta.verificacion_expira_en = (
            datetime.now(timezone.utc)
            - timedelta(hours=1)
        )
        session.commit()

    token = extraer_token(enlaces[0])

    respuesta = client.post(
        "/auth/verificar-correo",
        json={"token": token},
    )

    assert respuesta.status_code == 400
    assert login(client).status_code == 403


def test_reenviar_invalida_enlace_anterior(
    entorno_verificacion, monkeypatch
):
    client, _, enlaces = entorno_verificacion

    # Eliminamos el tiempo mínimo solo para esta prueba.
    monkeypatch.setattr(
        settings, "email_verification_resend_seconds", 0
    )

    assert registrar(client).status_code == 201
    token_anterior = extraer_token(enlaces[0])

    respuesta = client.post(
        "/auth/reenviar-verificacion",
        json={"correo": "nuevo@example.com"},
    )

    assert respuesta.status_code == 200
    assert len(enlaces) == 2

    token_nuevo = extraer_token(enlaces[1])
    assert token_nuevo != token_anterior

    # El enlace anterior ya no debe funcionar.
    anterior = client.post(
        "/auth/verificar-correo",
        json={"token": token_anterior},
    )
    assert anterior.status_code == 400

    nuevo = client.post(
        "/auth/verificar-correo",
        json={"token": token_nuevo},
    )
    assert nuevo.status_code == 200



def test_fallo_envio_permite_reenvio(
    entorno_verificacion,
    monkeypatch,
):
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from app.models.cuenta import Cuenta
    from app.services.verificacion_correo import ErrorEnvioCorreo

    client, engine, enlaces_enviados = entorno_verificacion

    correo = "fallo.envio@example.com"

    # Simular que Resend no puede enviar el correo.
    def fallar_envio(destinatario, enlace):
        raise ErrorEnvioCorreo("Fallo simulado de Resend")

    monkeypatch.setattr(
        "app.services.verificacion_correo.enviar_correo",
        fallar_envio,
    )

    # La cuenta se crea, pero el envío falla.
    respuesta = client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuariofalloenvio",
            "correo": correo,
            "password": "ClavePrueba123",
        },
    )

    assert respuesta.status_code == 503

    # El fallo no debe dejar un token de envío pendiente.
    with Session(engine) as db:
        cuenta = db.scalar(
            select(Cuenta).where(Cuenta.correo == correo)
        )

        assert cuenta is not None
        assert cuenta.correo_verificado is False
        assert cuenta.verificacion_token_hash is None
        assert cuenta.verificacion_expira_en is None
        assert cuenta.verificacion_enviada_en is None

    # Restablecer el envío simulado para comprobar el reenvío.
    def enviar_correctamente(destinatario, enlace):
        enlaces_enviados.append(enlace)

    monkeypatch.setattr(
        "app.services.verificacion_correo.enviar_correo",
        enviar_correctamente,
    )

    respuesta_reenvio = client.post(
        "/auth/reenviar-verificacion",
        json={"correo": correo},
    )

    assert respuesta_reenvio.status_code == 200
    assert len(enlaces_enviados) == 1

    # Ahora sí debe existir un nuevo token válido.
    with Session(engine) as db:
        cuenta = db.scalar(
            select(Cuenta).where(Cuenta.correo == correo)
        )

        assert cuenta is not None
        assert cuenta.correo_verificado is False
        assert cuenta.verificacion_token_hash is not None
        assert cuenta.verificacion_expira_en is not None
        assert cuenta.verificacion_enviada_en is not None
