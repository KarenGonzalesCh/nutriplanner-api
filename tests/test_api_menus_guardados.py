
from sqlalchemy.orm import Session

from app.models.receta import Receta

from tests.test_recetas import (
    client,
    autenticar,
    crear_perfil,
    cargar_recetas,
)


def test_api_menu_crear_listar_consultar_y_eliminar(client):
    test_client, engine = client

    ids = cargar_recetas(engine)
    headers = autenticar(test_client)
    crear_perfil(test_client, headers)

    # Configurar las porciones de la receta de prueba.
    with Session(engine) as db:
        receta = db.get(Receta, ids["receta_arroz"])
        assert receta is not None
        receta.porciones_base = 1
        db.commit()

    datos = {
        "nombre": "Mi menú de prueba",
        "cantidad_dias": 1,
        "comensales": 2,
        "tamano_porcion": "NORMAL",
        "posiciones_seleccionadas": [
            {
                "dia": 1,
                "tipo_comida": "ALMUERZO",
            }
        ],
        "comidas": [
            {
                "dia": 1,
                "tipo_comida": "ALMUERZO",
                "receta_id": ids["receta_arroz"],
                "sustituciones": [],
            }
        ],
    }

    # Sin autenticación no se pueden consultar menús.
    respuesta = test_client.get("/menus")
    assert respuesta.status_code == 401

    # Guardar el menú.
    respuesta = test_client.post(
        "/menus",
        headers=headers,
        json=datos,
    )

    assert respuesta.status_code == 201, respuesta.text

    menu_id = respuesta.json()["id"]

    assert respuesta.json()["nombre"] == "Mi menú de prueba"
    assert len(respuesta.json()["comidas"]) == 1

    # Listar los menús guardados.
    respuesta = test_client.get(
        "/menus",
        headers=headers,
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1
    assert respuesta.json()[0]["id"] == menu_id

    # Consultar el detalle.
    respuesta = test_client.get(
        f"/menus/{menu_id}",
        headers=headers,
    )

    assert respuesta.status_code == 200

    comida = respuesta.json()["comidas"][0]

    assert comida["instantanea"]["nombre_receta"] == "Arroz hervido"

    # Rechazar un menú con una comida seleccionada
    # que todavía no tiene receta confirmada.
    datos["posiciones_seleccionadas"].append({
        "dia": 1,
        "tipo_comida": "CENA",
    })

    respuesta = test_client.post(
        "/menus",
        headers=headers,
        json=datos,
    )

    assert respuesta.status_code == 422

    # El menú inválido no se guardó.
    respuesta = test_client.get(
        "/menus",
        headers=headers,
    )

    assert len(respuesta.json()) == 1

    # Eliminar el menú original.
    respuesta = test_client.delete(
        f"/menus/{menu_id}",
        headers=headers,
    )

    assert respuesta.status_code == 204

    # Comprobar que ya no existe.
    respuesta = test_client.get(
        f"/menus/{menu_id}",
        headers=headers,
    )

    assert respuesta.status_code == 404
