
from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import obtener_cuenta_actual
from app.core.enums import TipoComida
from app.db.session import get_db
from app.models.cuenta import Cuenta
from app.models.menu import Menu
from app.schemas.menu import GuardarMenuRequest
from app.services.guardar_menu import (
    GuardarMenuService,
    MenuInvalidoError,
)


router = APIRouter(
    prefix="/menus",
    tags=["Menús guardados"],
)


# SOLICITUD PARA GUARDAR UN MENÚ

class PosicionSeleccionada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dia: int = Field(ge=1, le=7)
    tipo_comida: TipoComida


class GuardarMenuCompletoRequest(GuardarMenuRequest):
    posiciones_seleccionadas: list[PosicionSeleccionada] = Field(
        min_length=1
    )

    @model_validator(mode="after")
    def verificar_estructura_completa(self):
        esperadas = [
            (posicion.dia, posicion.tipo_comida)
            for posicion in self.posiciones_seleccionadas
        ]

        confirmadas = {
            (comida.dia, comida.tipo_comida)
            for comida in self.comidas
        }

        if any(
            dia > self.cantidad_dias
            for dia, _ in esperadas
        ):
            raise ValueError(
                "Hay comidas seleccionadas fuera del período"
            )

        if len(esperadas) != len(set(esperadas)):
            raise ValueError(
                "Hay comidas seleccionadas duplicadas"
            )

        if set(esperadas) != confirmadas:
            raise ValueError(
                "El menú tiene comidas seleccionadas sin confirmar"
            )

        return self


# RESPUESTAS DE LA API

class MenuResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    cantidad_dias: int
    comensales: int
    tamano_porcion: str
    fecha_creacion: datetime


class ComidaGuardada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dia: int
    tipo_comida: TipoComida
    receta_id: int
    instantanea: dict


class MenuDetalle(MenuResumen):
    comidas: list[ComidaGuardada]


# POST /menus - GUARDAR

@router.post(
    "",
    response_model=MenuDetalle,
    status_code=HTTPStatus.CREATED,
)
def guardar_menu_confirmado(
    datos: GuardarMenuCompletoRequest,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    try:
        servicio = GuardarMenuService(db)

        return servicio.guardar(
            cuenta_id=cuenta_actual.id,
            datos=datos,
        )

    except MenuInvalidoError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error


# GET /menus - LISTAR

@router.get(
    "",
    response_model=list[MenuResumen],
)
def listar_menus_guardados(
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    consulta = (
        select(Menu)
        .where(Menu.cuenta_id == cuenta_actual.id)
        .order_by(
            Menu.fecha_creacion.desc(),
            Menu.id.desc(),
        )
    )

    return list(db.scalars(consulta).all())


# GET /menus/{menu_id} - CONSULTAR DETALLE

@router.get(
    "/{menu_id}",
    response_model=MenuDetalle,
)
def obtener_menu_guardado(
    menu_id: int,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    consulta = (
        select(Menu)
        .where(
            Menu.id == menu_id,
            Menu.cuenta_id == cuenta_actual.id,
        )
        .options(selectinload(Menu.comidas))
    )

    menu = db.scalar(consulta)

    if menu is None:
        raise HTTPException(
            status_code=404,
            detail="Menú no encontrado",
        )

    return menu


# DELETE /menus/{menu_id} - ELIMINAR

@router.delete(
    "/{menu_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
def eliminar_menu_guardado(
    menu_id: int,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    menu = db.scalar(
        select(Menu).where(
            Menu.id == menu_id,
            Menu.cuenta_id == cuenta_actual.id,
        )
    )

    if menu is None:
        raise HTTPException(
            status_code=404,
            detail="Menú no encontrado",
        )

    db.delete(menu)
    db.commit()
