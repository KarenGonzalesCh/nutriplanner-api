
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import crear_token_acceso
from app.db.session import get_db
from app.repositories.cuenta import CuentaRepository
from app.schemas.auth import TokenResponse
from app.services.cuentas import (
    CuentaService,
    CredencialesInvalidasError,
    CorreoNoVerificadoError,
)
from app.services.verificacion_correo import (
    ErrorEnvioCorreo,
    confirmar_verificacion,
    enviar_verificacion,
)


router = APIRouter(prefix="/auth", tags=["Autenticación"])


# --------------------------------------------------
# ESQUEMAS DE VERIFICACIÓN
# --------------------------------------------------

class ConfirmarCorreoBody(BaseModel):
    token: str = Field(min_length=32, max_length=256)


class ReenviarVerificacionBody(BaseModel):
    correo: EmailStr


# --------------------------------------------------
# INICIO DE SESIÓN
# --------------------------------------------------

@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=HTTPStatus.OK,
)
def iniciar_sesion(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    servicio = CuentaService(db)

    try:
        cuenta = servicio.autenticar(
            correo=form_data.username,
            password=form_data.password,
        )

    except CorreoNoVerificadoError as error:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=str(error),
        ) from error

    except CredencialesInvalidasError as error:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    token = crear_token_acceso(cuenta.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )


# --------------------------------------------------
# CONFIRMAR CORREO ELECTRÓNICO
# --------------------------------------------------

@router.post(
    "/verificar-correo",
    status_code=HTTPStatus.OK,
)
def verificar_correo(
    datos: ConfirmarCorreoBody,
    db: Session = Depends(get_db),
):
    verificado = confirmar_verificacion(
        db=db,
        token=datos.token,
    )

    if not verificado:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=(
                "El enlace de verificación es inválido, "
                "ya fue utilizado o venció."
            ),
        )

    return {
        "mensaje": (
            "Correo electrónico verificado correctamente. "
            "Ya podés iniciar sesión."
        )
    }


# --------------------------------------------------
# REENVIAR CORREO DE VERIFICACIÓN
# --------------------------------------------------

@router.post(
    "/reenviar-verificacion",
    status_code=HTTPStatus.OK,
)
def reenviar_verificacion(
    datos: ReenviarVerificacionBody,
    db: Session = Depends(get_db),
):
    mensaje = (
        "Si existe una cuenta pendiente de verificación, "
        "recibirás un nuevo enlace de confirmación."
    )

    if not settings.email_verification_enabled:
        return {"mensaje": mensaje}

    repositorio = CuentaRepository(db)

    cuenta = repositorio.obtener_por_correo(
        str(datos.correo)
    )

    # No revelar si el correo está registrado.
    if cuenta is None or cuenta.correo_verificado:
        return {"mensaje": mensaje}

    if not settings.resend_api_key or not settings.email_from:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail="El servicio de correos no está disponible.",
        )

    try:
        enviar_verificacion(db, cuenta)

    except ErrorEnvioCorreo as error:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail=(
                "No se pudo enviar el enlace. "
                "Intentá nuevamente más tarde."
            ),
        ) from error

    return {"mensaje": mensaje}
