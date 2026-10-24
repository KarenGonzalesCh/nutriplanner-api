
from pydantic import BaseModel, ConfigDict

from app.core.enums import NivelDificultad, TipoComida


class RecetaIngredienteResponse(BaseModel):
    ingrediente_id: int
    nombre: str
    cantidad: float
    unidad: str


class RecetaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    pasos: str
    tiempo_preparacion: int
    dificultad: NivelDificultad
    info_nutricional: str | None
    tipos_comida: list[TipoComida]
    ingredientes: list[RecetaIngredienteResponse]

