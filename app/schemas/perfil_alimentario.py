
from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import NivelDificultad


class PerfilAlimentarioCreate(BaseModel):
    nivel_culinario: NivelDificultad = NivelDificultad.PRINCIPIANTE

    alergias_ids: list[int] = Field(default_factory=list)
    ingredientes_evitados_ids: list[int] = Field(default_factory=list)
    categorias_evitadas_ids: list[int] = Field(default_factory=list)


class PerfilAlimentarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cuenta_id: int
    nivel_culinario: NivelDificultad

    alergias_ids: list[int]
    ingredientes_evitados_ids: list[int]
    categorias_evitadas_ids: list[int]
