
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import TipoComida


class TamanoPorcion(str, Enum):
    PEQUENA = "PEQUENA"
    NORMAL = "NORMAL"
    GRANDE = "GRANDE"


class GenerarMenuRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cantidad_dias: int = Field(ge=1, le=7)
    tipos_comida: list[TipoComida] = Field(min_length=1)
    comensales: int = Field(gt=0)
    tamano_porcion: TamanoPorcion = TamanoPorcion.NORMAL

    @model_validator(mode="after")
    def validar_solicitud(self):
        if len(self.tipos_comida) != len(set(self.tipos_comida)):
            raise ValueError(
                "No se pueden repetir tipos de comida"
            )

        if self.tamano_porcion != TamanoPorcion.NORMAL:
            raise ValueError(
                "Por ahora solo se admite el tamaño NORMAL"
            )

        return self


class IngredienteEscaladoResponse(BaseModel):
    receta_ingrediente_id: int
    ingrediente_id: int
    cantidad: Decimal
    unidad: str


class ComidaPropuestaResponse(BaseModel):
    dia: int
    tipo_comida: TipoComida
    receta_id: int | None

    tiene_conflicto_flexible: bool = False
    requiere_sustituciones: bool = False

    ingredientes: list[IngredienteEscaladoResponse] = Field(
        default_factory=list
    )


class PropuestaMenuResponse(BaseModel):
    comidas: list[ComidaPropuestaResponse]
    estructura_completa: bool
