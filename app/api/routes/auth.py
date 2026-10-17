
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import crear_token_acceso
from app.db.session import get_db
from app.schemas.auth import TokenResponse
from app.services.cuentas import (
    CuentaService,
    CredencialesInvalidasError,
)


router = APIRouter(prefix="/auth", tags=["Autenticación"])


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
