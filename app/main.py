from fastapi import FastAPI

from app.core.config import settings

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
