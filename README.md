# NutriPlanner API

API REST de planificación alimentaria. Genera menús personalizados de 1 a 7 días
a partir de las alergias, los alimentos a evitar y el nivel culinario del usuario.

Construida con FastAPI y SQLAlchemy. La documentación de requerimientos está en
[`docs/requirements.md`](docs/requirements.md).

## Estructura

| Carpeta | Responsabilidad |
|---|---|
| `app/api/routes` | Endpoints (exposición HTTP) |
| `app/core` | Configuración y seguridad |
| `app/db` | Conexión y sesión de base de datos |
| `app/models` | Modelos SQLAlchemy |
| `app/schemas` | Esquemas Pydantic de entrada y salida |
| `app/repositories` | Acceso a datos |
| `app/services` | Lógica de negocio |
| `tests` | Pruebas automatizadas |

## Puesta en marcha

```bash
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Completar los valores sensibles
uvicorn app.main:app --reload
```

La documentación interactiva queda disponible en http://localhost:8000/docs.

## Docker

```bash
docker build -t nutriplanner-api .
docker run --env-file .env -p 8000:8000 nutriplanner-api
```

## Pruebas

```bash
pytest
```
