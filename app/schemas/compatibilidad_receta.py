from pydantic import BaseModel

from app.services.compatibilidad_receta import EstadoCompatibilidad


class AlternativaDisponibleResponse(BaseModel):
    id: int
    ingrediente_id: int
    nombre: str
    cantidad: float
    unidad: str


class IngredienteRestringidoResponse(BaseModel):
    receta_ingrediente_id: int
    ingrediente_id: int
    nombre: str
    alternativas_validas: list[AlternativaDisponibleResponse]


class CompatibilidadRecetaResponse(BaseModel):
    receta_id: int
    nombre: str
    estado_compatibilidad: EstadoCompatibilidad
    ingredientes_restringidos: list[IngredienteRestringidoResponse]
