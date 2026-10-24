
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def generar_hash(password: str) -> str:
    """Genera un hash seguro de la contraseña."""
    return password_hash.hash(password)


def verificar_password(
    password: str,
    password_hash_almacenado: str,
) -> bool:
    """Comprueba una contraseña contra su hash."""
    return password_hash.verify(
        password,
        password_hash_almacenado,
    )


def crear_token_acceso(cuenta_id: int) -> str:
    """Genera un JWT para una cuenta autenticada."""
    expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    datos = {
        "sub": str(cuenta_id),
        "exp": expiracion,
    }

    return jwt.encode(
        datos,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
