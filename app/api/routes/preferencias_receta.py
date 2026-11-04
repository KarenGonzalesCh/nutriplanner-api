
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import obtener_cuenta_actual
from app.db.session import get_db
from app.models.cuenta import Cuenta
from app.services.preferencias_receta import (
    PreferenciasRecetaService,
    RecetaNoExisteError,
)


router = APIRouter(
    prefix="/recetas",
    tags=["Preferencias de recetas"],
)


# FAVORITAS

@router.get(
    "/favoritas",
    response_model=list[int],
    status_code=HTTPStatus.OK,
)
def listar_favoritas(
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = PreferenciasRecetaService(db)
    return servicio.listar_favoritas(cuenta_actual.id)


@router.post(
    "/{receta_id}/favorita",
    status_code=HTTPStatus.NO_CONTENT,
)
def agregar_favorita(
    receta_id: int,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = PreferenciasRecetaService(db)

    try:
        servicio.agregar_favorita(cuenta_actual.id, receta_id)

    except RecetaNoExisteError as error:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    "/{receta_id}/favorita",
    status_code=HTTPStatus.NO_CONTENT,
)
def quitar_favorita(
    receta_id: int,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = PreferenciasRecetaService(db)

    eliminada = servicio.quitar_favorita(cuenta_actual.id, receta_id)

    if not eliminada:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="La receta no está en favoritas",
        )


# EXCLUSIONES

@router.get(
    "/excluidas",
    response_model=list[int],
    status_code=HTTPStatus.OK,
)
def listar_excluidas(
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = PreferenciasRecetaService(db)
    return servicio.listar_excluidas(cuenta_actual.id)


@router.post(
    "/{receta_id}/exclusion",
    status_code=HTTPStatus.NO_CONTENT,
)
def agregar_exclusion(
    receta_id: int,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = PreferenciasRecetaService(db)

    try:
        servicio.agregar_exclusion(cuenta_actual.id, receta_id)

    except RecetaNoExisteError as error:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    "/{receta_id}/exclusion",
    status_code=HTTPStatus.NO_CONTENT,
)
def quitar_exclusion(
    receta_id: int,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = PreferenciasRecetaService(db)

    eliminada = servicio.quitar_exclusion(cuenta_actual.id, receta_id)

    if not eliminada:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="La receta no está excluida",
        )
