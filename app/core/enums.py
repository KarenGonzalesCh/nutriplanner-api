
from enum import Enum


class Rol(str, Enum):
    USUARIO = "USUARIO"
    MODERADOR = "MODERADOR"


class NivelDificultad(str, Enum):
    PRINCIPIANTE = "PRINCIPIANTE"
    INTERMEDIO = "INTERMEDIO"
    AVANZADO = "AVANZADO"


class TipoComida(str, Enum):
    DESAYUNO = "DESAYUNO"
    ALMUERZO = "ALMUERZO"
    MERIENDA = "MERIENDA"
    CENA = "CENA"


class EstadoReporte(str, Enum):
    PENDIENTE = "PENDIENTE"
    CERRADO = "CERRADO"
    ACEPTADO = "ACEPTADO"
