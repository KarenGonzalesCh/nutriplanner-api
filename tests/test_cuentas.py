from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.cuenta import Cuenta
from app.schemas.cuenta import CuentaCreate
from app.services.cuentas import CuentaService, CredencialesInvalidasError

import jwt

from app.core.config import settings

from datetime import datetime, timedelta, timezone

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




def test_registrar_cuenta(client):
    test_client, engine = client

    response = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_test",
            "correo": "test@example.com",
            "password": "ClaveSegura123",
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    datos = response.json()

    assert datos["nombre_usuario"] == "usuario_test"
    assert datos["correo"] == "test@example.com"
    assert datos["rol"] == "USUARIO"
    assert "password_hash" not in datos
    assert "password" not in datos

    with Session(engine) as session:
        cuenta = session.get(Cuenta, datos["id"])

        assert cuenta is not None
        assert cuenta.password_hash != "ClaveSegura123"
        assert cuenta.password_hash.startswith("$argon2")


def test_registrar_cuenta_correo_duplicado(client):
    test_client, _ = client

    primera_respuesta = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_uno",
            "correo": "duplicado@example.com",
            "password": "ClaveSegura123",
        },
    )

    segunda_respuesta = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_dos",
            "correo": "duplicado@example.com",
            "password": "OtraClave123",
        },
    )

    assert primera_respuesta.status_code == HTTPStatus.CREATED
    assert segunda_respuesta.status_code == HTTPStatus.CONFLICT
    assert segunda_respuesta.json()["detail"] == (
        "El correo ya está registrado"
    )


def test_registrar_cuenta_nombre_duplicado(client):
    test_client, _ = client

    primera_respuesta = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_repetido",
            "correo": "primero@example.com",
            "password": "ClaveSegura123",
        },
    )

    segunda_respuesta = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_repetido",
            "correo": "segundo@example.com",
            "password": "OtraClave123",
        },
    )

    assert primera_respuesta.status_code == HTTPStatus.CREATED
    assert segunda_respuesta.status_code == HTTPStatus.CONFLICT
    assert segunda_respuesta.json()["detail"] == (
        "El nombre de usuario ya está registrado"
    )



def test_registrar_cuenta_password_corta(client):
    test_client, _ = client

    response = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_nuevo",
            "correo": "nuevo@example.com",
            "password": "1234",
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY



def test_registrar_cuenta_correo_invalido(client):
    test_client, _ = client

    response = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_nuevo",
            "correo": "correo_invalido",
            "password": "ClaveSegura123",
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY



def test_autenticar_cuenta_correctamente(client):
    _, engine = client

    with Session(engine) as session:
        servicio = CuentaService(session)

        datos = CuentaCreate(
            nombre_usuario="usuario_login",
            correo="login@example.com",
            password="ClaveSegura123",
        )

        cuenta_registrada = servicio.registrar(datos)

        cuenta_autenticada = servicio.autenticar(
            correo="login@example.com",
            password="ClaveSegura123",
        )

        assert cuenta_autenticada.id == cuenta_registrada.id
        assert cuenta_autenticada.correo == "login@example.com"



def test_autenticar_password_incorrecta(client):
    _, engine = client

    with Session(engine) as session:
        servicio = CuentaService(session)

        datos = CuentaCreate(
            nombre_usuario="usuario_login",
            correo="login@example.com",
            password="ClaveSegura123",
        )

        servicio.registrar(datos)

        with pytest.raises(
            CredencialesInvalidasError,
            match="Credenciales incorrectas",
        ):
            servicio.autenticar(
                correo="login@example.com",
                password="ClaveIncorrecta123",
            )



def test_autenticar_correo_inexistente(client):
    _, engine = client

    with Session(engine) as session:
        servicio = CuentaService(session)

        with pytest.raises(
            CredencialesInvalidasError,
            match="Credenciales incorrectas",
        ):
            servicio.autenticar(
                correo="noexiste@example.com",
                password="ClaveSegura123",
            )



def test_login_devuelve_token_jwt(client):
    test_client, _ = client

    # Primero registramos una cuenta
    registro = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_jwt",
            "correo": "jwt@example.com",
            "password": "ClaveSegura123",
        },
    )

    assert registro.status_code == HTTPStatus.CREATED

    # Después iniciamos sesión
    respuesta = test_client.post(
        "/auth/token",
        data={
            "username": "jwt@example.com",
            "password": "ClaveSegura123",
        },
    )

    assert respuesta.status_code == HTTPStatus.OK

    datos = respuesta.json()

    assert datos["token_type"] == "bearer"
    assert "access_token" in datos

    # Verificamos la firma y el contenido del JWT
    contenido = jwt.decode(
        datos["access_token"],
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    assert contenido["sub"] == str(registro.json()["id"])
    assert "exp" in contenido



def test_login_password_incorrecta(client):
    test_client, _ = client

    # Registramos una cuenta
    registro = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_login_error",
            "correo": "error@example.com",
            "password": "ClaveSegura123",
        },
    )

    assert registro.status_code == HTTPStatus.CREATED

    # Intentamos ingresar con una contraseña incorrecta
    respuesta = test_client.post(
        "/auth/token",
        data={
            "username": "error@example.com",
            "password": "ClaveIncorrecta123",
        },
    )

    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED
    assert respuesta.json()["detail"] == "Credenciales incorrectas"
    assert respuesta.headers["www-authenticate"] == "Bearer"



def test_login_correo_inexistente(client):
    test_client, _ = client

    respuesta = test_client.post(
        "/auth/token",
        data={
            "username": "noexiste@example.com",
            "password": "ClaveSegura123",
        },
    )

    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED
    assert respuesta.json()["detail"] == "Credenciales incorrectas"
    assert respuesta.headers["www-authenticate"] == "Bearer"
    assert "access_token" not in respuesta.json()



def test_obtener_mi_cuenta_con_token_valido(client):
    test_client, _ = client

    # Registramos una cuenta
    registro = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_privado",
            "correo": "privado@example.com",
            "password": "ClaveSegura123",
        },
    )

    assert registro.status_code == HTTPStatus.CREATED

    # Iniciamos sesión para obtener el JWT
    login = test_client.post(
        "/auth/token",
        data={
            "username": "privado@example.com",
            "password": "ClaveSegura123",
        },
    )

    assert login.status_code == HTTPStatus.OK

    token = login.json()["access_token"]

    # Consultamos la cuenta utilizando el token
    respuesta = test_client.get(
        "/cuentas/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert respuesta.status_code == HTTPStatus.OK

    datos = respuesta.json()

    assert datos["id"] == registro.json()["id"]
    assert datos["nombre_usuario"] == "usuario_privado"
    assert datos["correo"] == "privado@example.com"
    assert datos["rol"] == "USUARIO"

    assert "password" not in datos
    assert "password_hash" not in datos



def test_obtener_mi_cuenta_sin_token(client):
    test_client, _ = client

    respuesta = test_client.get("/cuentas/me")

    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED
    assert "access_token" not in respuesta.json()


def test_obtener_mi_cuenta_token_invalido(client):
    test_client, _ = client

    respuesta = test_client.get(
        "/cuentas/me",
        headers={
            "Authorization": "Bearer token_invalido"
        },
    )

    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED
    assert respuesta.json()["detail"] == (
        "No se pudieron validar las credenciales"
    )
    assert respuesta.headers["www-authenticate"] == "Bearer"



def test_obtener_mi_cuenta_token_vencido(client):
    test_client, _ = client

    # Generamos un JWT cuya fecha de vencimiento ya pasó
    expiracion = datetime.now(timezone.utc) - timedelta(minutes=5)

    token_vencido = jwt.encode(
        {
            "sub": "1",
            "exp": expiracion,
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    respuesta = test_client.get(
        "/cuentas/me",
        headers={
            "Authorization": f"Bearer {token_vencido}"
        },
    )

    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED
    assert respuesta.json()["detail"] == (
        "No se pudieron validar las credenciales"
    )
    assert respuesta.headers["www-authenticate"] == "Bearer"
