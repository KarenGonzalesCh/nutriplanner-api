
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
from app.models.ingrediente import Ingrediente
from app.models.categoria_alimento import CategoriaAlimento


@pytest.fixture
def client():
    # Crear una base SQLite temporal para cada test
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


def registrar_y_autenticar(client):
    # Registrar una cuenta de prueba
    registro = client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_perfil",
            "correo": "perfil@example.com",
            "password": "ClaveSegura123",
        },
    )

    assert registro.status_code == HTTPStatus.CREATED

    # Iniciar sesión y obtener el token JWT
    login = client.post(
        "/auth/token",
        data={
            "username": "perfil@example.com",
            "password": "ClaveSegura123",
        },
    )

    assert login.status_code == HTTPStatus.OK

    token = login.json()["access_token"]

    return registro.json()["id"], {
        "Authorization": f"Bearer {token}"
    }


def test_obtener_perfil_sin_autenticacion(client):
    test_client, _ = client

    response = test_client.get("/perfil/me")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_crear_perfil_autenticado(client):
    test_client, _ = client

    cuenta_id, headers = registrar_y_autenticar(test_client)

    respuesta = test_client.post(
        "/perfil",
        headers=headers,
        json={
            "nivel_culinario": "PRINCIPIANTE",
            "alergias_ids": [],
            "ingredientes_evitados_ids": [],
            "categorias_evitadas_ids": [],
        },
    )

    assert respuesta.status_code == HTTPStatus.CREATED

    datos = respuesta.json()

    assert datos["cuenta_id"] == cuenta_id
    assert datos["nivel_culinario"] == "PRINCIPIANTE"
    assert datos["alergias_ids"] == []
    assert datos["ingredientes_evitados_ids"] == []
    assert datos["categorias_evitadas_ids"] == []


def test_obtener_perfil_autenticado(client):
    test_client, _ = client

    # Registrar un usuario y obtener su JWT
    cuenta_id, headers = registrar_y_autenticar(test_client)

    # Crear su perfil alimentario
    creacion = test_client.post(
        "/perfil",
        headers=headers,
        json={
            "nivel_culinario": "INTERMEDIO",
            "alergias_ids": [],
            "ingredientes_evitados_ids": [],
            "categorias_evitadas_ids": [],
        },
    )

    assert creacion.status_code == HTTPStatus.CREATED

    # Consultar el perfil creado
    respuesta = test_client.get(
        "/perfil/me",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.OK

    datos = respuesta.json()

    assert datos["id"] == creacion.json()["id"]
    assert datos["cuenta_id"] == cuenta_id
    assert datos["nivel_culinario"] == "INTERMEDIO"
    assert datos["alergias_ids"] == []
    assert datos["ingredientes_evitados_ids"] == []
    assert datos["categorias_evitadas_ids"] == []


def test_no_permitir_perfil_duplicado(client):
    test_client, _ = client

    # Registrar una cuenta y obtener su JWT
    _, headers = registrar_y_autenticar(test_client)

    perfil = {
        "nivel_culinario": "PRINCIPIANTE",
        "alergias_ids": [],
        "ingredientes_evitados_ids": [],
        "categorias_evitadas_ids": [],
    }

    # Crear el primer perfil
    primera_respuesta = test_client.post(
        "/perfil",
        headers=headers,
        json=perfil,
    )

    assert primera_respuesta.status_code == HTTPStatus.CREATED

    # Intentar crear otro perfil para la misma cuenta
    segunda_respuesta = test_client.post(
        "/perfil",
        headers=headers,
        json=perfil,
    )

    assert segunda_respuesta.status_code == HTTPStatus.CONFLICT
    assert "ya tiene un perfil" in segunda_respuesta.json()["detail"]


def test_actualizar_perfil_alimentario(client):
    test_client, _ = client

    # Registrar una cuenta y obtener su JWT
    cuenta_id, headers = registrar_y_autenticar(test_client)

    # Crear el perfil inicial
    creacion = test_client.post(
        "/perfil",
        headers=headers,
        json={
            "nivel_culinario": "PRINCIPIANTE",
            "alergias_ids": [],
            "ingredientes_evitados_ids": [],
            "categorias_evitadas_ids": [],
        },
    )

    assert creacion.status_code == HTTPStatus.CREATED

    # Actualizar el nivel culinario
    actualizacion = test_client.put(
        "/perfil/me",
        headers=headers,
        json={
            "nivel_culinario": "AVANZADO",
            "alergias_ids": [],
            "ingredientes_evitados_ids": [],
            "categorias_evitadas_ids": [],
        },
    )

    assert actualizacion.status_code == HTTPStatus.OK

    datos = actualizacion.json()

    assert datos["id"] == creacion.json()["id"]
    assert datos["cuenta_id"] == cuenta_id
    assert datos["nivel_culinario"] == "AVANZADO"

    # Consultar nuevamente para verificar que se guardó
    consulta = test_client.get(
        "/perfil/me",
        headers=headers,
    )

    assert consulta.status_code == HTTPStatus.OK
    assert consulta.json()["nivel_culinario"] == "AVANZADO"


def test_crear_perfil_con_alergia_inexistente(client):
    test_client, _ = client

    _, headers = registrar_y_autenticar(test_client)

    respuesta = test_client.post(
        "/perfil",
        headers=headers,
        json={
            "nivel_culinario": "PRINCIPIANTE",
            "alergias_ids": [999],
            "ingredientes_evitados_ids": [],
            "categorias_evitadas_ids": [],
        },
    )

    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "alergias inexistentes" in respuesta.json()["detail"]


def test_crear_perfil_con_ingrediente_inexistente(client):
    test_client, _ = client

    _, headers = registrar_y_autenticar(test_client)

    respuesta = test_client.post(
        "/perfil",
        headers=headers,
        json={
            "nivel_culinario": "PRINCIPIANTE",
            "alergias_ids": [],
            "ingredientes_evitados_ids": [999],
            "categorias_evitadas_ids": [],
        },
    )

    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "ingredientes inexistentes" in respuesta.json()["detail"]



def test_crear_perfil_con_categoria_inexistente(client):
    test_client, _ = client

    _, headers = registrar_y_autenticar(test_client)

    respuesta = test_client.post(
        "/perfil",
        headers=headers,
        json={
            "nivel_culinario": "PRINCIPIANTE",
            "alergias_ids": [],
            "ingredientes_evitados_ids": [],
            "categorias_evitadas_ids": [999],
        },
    )

    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "categorías inexistentes" in respuesta.json()["detail"]



def test_cada_usuario_consulta_su_propio_perfil(client):
    test_client, _ = client

    # Registrar y autenticar al primer usuario
    cuenta_1, headers_1 = registrar_y_autenticar(test_client)

    # Registrar al segundo usuario
    registro_2 = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_dos",
            "correo": "usuario2@example.com",
            "password": "ClaveSegura456",
        },
    )
    assert registro_2.status_code == HTTPStatus.CREATED
    cuenta_2 = registro_2.json()["id"]

    # Autenticar al segundo usuario
    login_2 = test_client.post(
        "/auth/token",
        data={
            "username": "usuario2@example.com",
            "password": "ClaveSegura456",
        },
    )
    assert login_2.status_code == HTTPStatus.OK

    headers_2 = {
        "Authorization": f"Bearer {login_2.json()['access_token']}"
    }

    # Crear un perfil diferente para cada usuario
    perfil_1 = test_client.post(
        "/perfil",
        headers=headers_1,
        json={"nivel_culinario": "PRINCIPIANTE"},
    )
    perfil_2 = test_client.post(
        "/perfil",
        headers=headers_2,
        json={"nivel_culinario": "AVANZADO"},
    )

    assert perfil_1.status_code == HTTPStatus.CREATED
    assert perfil_2.status_code == HTTPStatus.CREATED

    # Consultar usando el token de cada cuenta
    consulta_1 = test_client.get("/perfil/me", headers=headers_1)
    consulta_2 = test_client.get("/perfil/me", headers=headers_2)

    assert consulta_1.status_code == HTTPStatus.OK
    assert consulta_2.status_code == HTTPStatus.OK

    assert consulta_1.json()["cuenta_id"] == cuenta_1
    assert consulta_1.json()["nivel_culinario"] == "PRINCIPIANTE"
    assert consulta_1.json()["id"] == perfil_1.json()["id"]

    assert consulta_2.json()["cuenta_id"] == cuenta_2
    assert consulta_2.json()["nivel_culinario"] == "AVANZADO"
    assert consulta_2.json()["id"] == perfil_2.json()["id"]

    assert cuenta_1 != cuenta_2
    assert perfil_1.json()["id"] != perfil_2.json()["id"]


def test_actualizar_perfil_no_modifica_otro_usuario(client):
    test_client, _ = client

    # Crear y autenticar al primer usuario
    cuenta_1, headers_1 = registrar_y_autenticar(test_client)

    # Crear y autenticar al segundo usuario
    registro_2 = test_client.post(
        "/cuentas",
        json={
            "nombre_usuario": "usuario_dos",
            "correo": "usuario2@example.com",
            "password": "ClaveSegura456",
        },
    )
    assert registro_2.status_code == HTTPStatus.CREATED
    cuenta_2 = registro_2.json()["id"]

    login_2 = test_client.post(
        "/auth/token",
        data={
            "username": "usuario2@example.com",
            "password": "ClaveSegura456",
        },
    )
    assert login_2.status_code == HTTPStatus.OK

    headers_2 = {
        "Authorization": f"Bearer {login_2.json()['access_token']}"
    }

    # Crear perfiles diferentes
    perfil_1 = test_client.post(
        "/perfil",
        headers=headers_1,
        json={"nivel_culinario": "PRINCIPIANTE"},
    )
    perfil_2 = test_client.post(
        "/perfil",
        headers=headers_2,
        json={"nivel_culinario": "INTERMEDIO"},
    )

    assert perfil_1.status_code == HTTPStatus.CREATED
    assert perfil_2.status_code == HTTPStatus.CREATED

    # El primer usuario actualiza su perfil
    actualizacion = test_client.put(
        "/perfil/me",
        headers=headers_1,
        json={"nivel_culinario": "AVANZADO"},
    )

    assert actualizacion.status_code == HTTPStatus.OK

    # Consultar ambos perfiles nuevamente
    consulta_1 = test_client.get("/perfil/me", headers=headers_1)
    consulta_2 = test_client.get("/perfil/me", headers=headers_2)

    assert consulta_1.status_code == HTTPStatus.OK
    assert consulta_2.status_code == HTTPStatus.OK

    # El primer perfil cambió
    assert consulta_1.json()["cuenta_id"] == cuenta_1
    assert consulta_1.json()["nivel_culinario"] == "AVANZADO"

    # El segundo perfil conserva sus datos originales
    assert consulta_2.json()["cuenta_id"] == cuenta_2
    assert consulta_2.json()["nivel_culinario"] == "INTERMEDIO"
    assert consulta_2.json()["id"] == perfil_2.json()["id"]


def test_obtener_perfil_inexistente(client):
    test_client, _ = client

    # Registrar y autenticar al usuario, sin crear su perfil
    _, headers = registrar_y_autenticar(test_client)

    respuesta = test_client.get(
        "/perfil/me",
        headers=headers,
    )

    assert respuesta.status_code == HTTPStatus.NOT_FOUND
    assert "no tiene un perfil alimentario" in respuesta.json()["detail"]


def test_actualizar_perfil_inexistente(client):
    test_client, _ = client

    # Registrar y autenticar al usuario, sin crear su perfil
    _, headers = registrar_y_autenticar(test_client)

    respuesta = test_client.put(
        "/perfil/me",
        headers=headers,
        json={
            "nivel_culinario": "INTERMEDIO",
            "alergias_ids": [],
            "ingredientes_evitados_ids": [],
            "categorias_evitadas_ids": [],
        },
    )

    assert respuesta.status_code == HTTPStatus.NOT_FOUND
    assert "no tiene un perfil alimentario" in respuesta.json()["detail"]


def test_crear_perfil_con_nivel_culinario_invalido(client):
    test_client, _ = client

    _, headers = registrar_y_autenticar(test_client)

    respuesta = test_client.post(
        "/perfil",
        headers=headers,
        json={
            "nivel_culinario": "EXPERTO",
            "alergias_ids": [],
            "ingredientes_evitados_ids": [],
            "categorias_evitadas_ids": [],
        },
    )

    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # Verificar que no se haya creado ningún perfil
    consulta = test_client.get(
        "/perfil/me",
        headers=headers,
    )

    assert consulta.status_code == HTTPStatus.NOT_FOUND


def test_crear_perfil_con_restricciones_validas(client):
    test_client, engine = client

    # Crear elementos reales en los catálogos
    with Session(engine) as session:
        categoria = CategoriaAlimento(nombre="Lacteos")
        alergia = Alergia(nombre="Proteina de leche")

        session.add_all([categoria, alergia])
        session.flush()

        ingrediente = Ingrediente(
            nombre="Leche",
            categoria_id=categoria.id,
        )

        session.add(ingrediente)
        session.commit()

        categoria_id = categoria.id
        alergia_id = alergia.id
        ingrediente_id = ingrediente.id

    # Registrar y autenticar al usuario
    _, headers = registrar_y_autenticar(test_client)

    # Crear un perfil utilizando IDs existentes
    respuesta = test_client.post(
        "/perfil",
        headers=headers,
        json={
            "nivel_culinario": "INTERMEDIO",
            "alergias_ids": [alergia_id],
            "ingredientes_evitados_ids": [ingrediente_id],
            "categorias_evitadas_ids": [categoria_id],
        },
    )

    assert respuesta.status_code == HTTPStatus.CREATED

    datos = respuesta.json()

    assert datos["nivel_culinario"] == "INTERMEDIO"
    assert datos["alergias_ids"] == [alergia_id]
    assert datos["ingredientes_evitados_ids"] == [ingrediente_id]
    assert datos["categorias_evitadas_ids"] == [categoria_id]

    # Comprobar que las restricciones quedaron guardadas
    consulta = test_client.get("/perfil/me", headers=headers)

    assert consulta.status_code == HTTPStatus.OK
    assert consulta.json()["alergias_ids"] == [alergia_id]
    assert consulta.json()["ingredientes_evitados_ids"] == [ingrediente_id]
    assert consulta.json()["categorias_evitadas_ids"] == [categoria_id]



def test_actualizar_restricciones_alimentarias(client):
    test_client, engine = client

    # Crear datos en los catálogos
    with Session(engine) as session:
        categoria = CategoriaAlimento(nombre="Lacteos")
        alergia_1 = Alergia(nombre="Proteina de leche")
        alergia_2 = Alergia(nombre="Huevo")

        session.add_all([categoria, alergia_1, alergia_2])
        session.flush()

        ingrediente = Ingrediente(
            nombre="Leche",
            categoria_id=categoria.id,
        )
        session.add(ingrediente)
        session.flush()

        categoria_id = categoria.id
        alergia_1_id = alergia_1.id
        alergia_2_id = alergia_2.id
        ingrediente_id = ingrediente.id

        session.commit()

    _, headers = registrar_y_autenticar(test_client)

    # Crear un perfil con restricciones iniciales
    creacion = test_client.post(
        "/perfil",
        headers=headers,
        json={
            "nivel_culinario": "PRINCIPIANTE",
            "alergias_ids": [alergia_1_id],
            "ingredientes_evitados_ids": [ingrediente_id],
            "categorias_evitadas_ids": [categoria_id],
        },
    )

    assert creacion.status_code == HTTPStatus.CREATED

    # Reemplazar las restricciones anteriores
    actualizacion = test_client.put(
        "/perfil/me",
        headers=headers,
        json={
            "nivel_culinario": "AVANZADO",
            "alergias_ids": [alergia_2_id],
            "ingredientes_evitados_ids": [],
            "categorias_evitadas_ids": [],
        },
    )

    assert actualizacion.status_code == HTTPStatus.OK

    # Consultar nuevamente para verificar los cambios
    consulta = test_client.get("/perfil/me", headers=headers)

    assert consulta.status_code == HTTPStatus.OK

    datos = consulta.json()

    assert datos["id"] == creacion.json()["id"]
    assert datos["nivel_culinario"] == "AVANZADO"
    assert datos["alergias_ids"] == [alergia_2_id]
    assert datos["ingredientes_evitados_ids"] == []
    assert datos["categorias_evitadas_ids"] == []
