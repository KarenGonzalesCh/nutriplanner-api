
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.cuenta import CuentaCreate, CuentaResponse
from app.services.cuentas import CuentaService, CuentaYaExisteError

from app.api.dependencies import obtener_cuenta_actual
from app.models.cuenta import Cuenta
from app.core.config import settings
from app.services.verificacion_correo import (
    ErrorEnvioCorreo,
    enviar_verificacion,
)


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
    # Evitar crear cuentas pendientes si el servicio
    # de envío de correos todavía no está configurado.
    if settings.email_verification_enabled:
        if not settings.resend_api_key or not settings.email_from:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail=(
                    "El servicio de verificación de correo "
                    "todavía no está configurado."
                ),
            )

    servicio = CuentaService(db)

    try:
        # Crear la cuenta.
        cuenta = servicio.registrar(datos)

    except CuentaYaExisteError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(error),
        ) from error

    # Enviar confirmación únicamente cuando
    # esté activada la verificación.
    if settings.email_verification_enabled:
        try:
            enviar_verificacion(db, cuenta)

        except ErrorEnvioCorreo as error:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail=(
                    "La cuenta fue creada, pero no pudimos "
                    "enviar el correo de confirmación. "
                    "Solicitá un nuevo enlace."
                ),
            ) from error

    return cuenta

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
