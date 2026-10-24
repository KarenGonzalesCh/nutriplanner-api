
from http import HTTPStatus

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_devuelve_ok():
    response = client.get("/health")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}
