
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.cuenta import CuentaCreate, CuentaResponse
from app.services.cuentas import CuentaService, CuentaYaExisteError

from app.api.dependencies import obtener_cuenta_actual
from app.models.cuenta import Cuenta


router = APIRouter(prefix="/cuentas", tags=["Cuentas"])


@router.post(
    "",
    response_model=CuentaResponse,
    status_code=HTTPStatus.CREATED,
)
def registrar_cuenta(
    datos: CuentaCreate,
    db: Session = Depends(get_db),
):
    servicio = CuentaService(db)

    try:
        return servicio.registrar(datos)
    except CuentaYaExisteError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(error),
        ) from error



@router.get(
    "/me",
    response_model=CuentaResponse,
    status_code=HTTPStatus.OK,
)
def obtener_mi_cuenta(
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
):
    """Devuelve la información de la cuenta autenticada."""
    return cuenta_actual
