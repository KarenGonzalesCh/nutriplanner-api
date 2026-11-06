
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


class SustitucionComidaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receta_ingrediente_id: int = Field(gt=0)
    alternativa_id: int = Field(gt=0)


class ComidaConfirmadaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dia: int = Field(ge=1, le=7)
    tipo_comida: TipoComida
    receta_id: int = Field(gt=0)

    sustituciones: list[SustitucionComidaRequest] = Field(
        default_factory=list
    )

    confirma_conflicto_flexible: bool = False
    confirma_receta_excluida: bool = False

    @model_validator(mode="after")
    def validar_sustituciones(self):
        posiciones = [
            item.receta_ingrediente_id
            for item in self.sustituciones
        ]

        if len(posiciones) != len(set(posiciones)):
            raise ValueError(
                "No se puede sustituir dos veces "
                "la misma posición de ingrediente"
            )

        return self


class GuardarMenuRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120)
    cantidad_dias: int = Field(ge=1, le=7)
    comensales: int = Field(gt=0)
    tamano_porcion: TamanoPorcion = TamanoPorcion.NORMAL

    comidas: list[ComidaConfirmadaRequest] = Field(
        min_length=1
    )

    @model_validator(mode="after")
    def validar_menu(self):
        if not self.nombre.strip():
            raise ValueError(
                "El menú debe tener un nombre"
            )

        if self.tamano_porcion != TamanoPorcion.NORMAL:
            raise ValueError(
                "Por ahora solo se admite el tamaño NORMAL"
            )

        posiciones = set()

        for comida in self.comidas:
            if comida.dia > self.cantidad_dias:
                raise ValueError(
                    "Una comida excede la cantidad de días"
                )

            clave = (comida.dia, comida.tipo_comida)

            if clave in posiciones:
                raise ValueError(
                    "No se puede repetir una comida "
                    "en el mismo día"
                )

            posiciones.add(clave)

        return self

