
from http import HTTPStatus

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.cuenta import Cuenta
from app.repositories.cuenta import CuentaRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def obtener_cuenta_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Cuenta:
    error_credenciales = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        cuenta_id = int(payload["sub"])

    except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
        raise error_credenciales

    repository = CuentaRepository(db)
    cuenta = repository.obtener_por_id(cuenta_id)

    if cuenta is None:
        raise error_credenciales

    return cuenta
