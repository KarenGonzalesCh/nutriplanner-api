
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.core.enums import Rol


class CuentaCreate(BaseModel):
    nombre_usuario: str = Field(min_length=3, max_length=50)
    correo: EmailStr
    password: str = Field(min_length=8)


class CuentaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_usuario: str
    correo: str
    rol: Rol
