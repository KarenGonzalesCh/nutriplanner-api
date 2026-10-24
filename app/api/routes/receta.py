
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import obtener_cuenta_actual
from app.db.session import get_db
from app.models.cuenta import Cuenta
from app.schemas.receta import RecetaResponse
from app.services.receta import (
    RecetaService,
    RecetaNoEncontradaError,
    PerfilRequeridoError,
)


router = APIRouter(
    prefix="/recetas",
    tags=["Recetas"],
)


@router.get(
    "",
    response_model=list[RecetaResponse],
    status_code=HTTPStatus.OK,
)
def listar_recetas(
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = RecetaService(db)

    try:
        return servicio.listar(cuenta_actual.id)

    except PerfilRequeridoError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/{receta_id}",
    response_model=RecetaResponse,
    status_code=HTTPStatus.OK,
)
def obtener_receta(
    receta_id: int,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = RecetaService(db)

    try:
        return servicio.obtener_por_id(
            cuenta_actual.id,
            receta_id,
        )

    except PerfilRequeridoError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(error),
        ) from error

    except RecetaNoEncontradaError as error:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=str(error),
        ) from error
