
from pydantic import BaseModel, Field


class SeleccionarSustitucionRequest(BaseModel):
    """Alternativa seleccionada por el usuario."""

    alternativa_id: int = Field(gt=0)


class SustitucionGuardadaResponse(BaseModel):
    """Información de una sustitución guardada."""

    receta_id: int
    receta_ingrediente_id: int
    alternativa_id: int
    ingrediente_alternativo_id: int
    nombre: str
    cantidad: float
    unidad: str
