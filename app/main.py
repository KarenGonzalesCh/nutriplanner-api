from fastapi import FastAPI

from app.core.config import settings
from app.schemas.health import HealthResponse
from app.api.routes.cuentas import router as cuentas_router
from app.api.routes.auth import router as auth_router
from app.api.routes.perfil_alimentario import router as perfil_router
from app.api.routes.alergia import router as alergias_router
from app.api.routes.categoria_alimento import router as categorias_router
from app.api.routes.ingrediente import router as ingredientes_router
from app.api.routes.receta import router as receta_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API de planificación alimentaria: genera menús personalizados "
    "según alergias, alimentos a evitar y nivel culinario.",
)


@app.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    """Verifica que la API está en funcionamiento."""
    return {"status": "ok"}


app.include_router(cuentas_router)

app.include_router(auth_router)

app.include_router(perfil_router)

app.include_router(alergias_router)

app.include_router(categorias_router)

app.include_router(ingredientes_router)

app.include_router(receta_router)