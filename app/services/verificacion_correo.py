
"""Servicio para enviar y confirmar correos electrónicos."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from html import escape
from urllib.parse import quote

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.cuenta import Cuenta


class ErrorEnvioCorreo(Exception):
    """No se pudo enviar el correo de confirmación."""


def ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


def normalizar_utc(fecha: datetime) -> datetime:
    """Compatible con fechas SQLite sin zona horaria."""
    if fecha.tzinfo is None:
        return fecha.replace(tzinfo=timezone.utc)
    return fecha.astimezone(timezone.utc)


def generar_token() -> str:
    """Genera un token criptográficamente seguro."""
    return secrets.token_urlsafe(32)


def obtener_hash_token(token: str) -> str:
    """Guarda un hash en lugar del token original."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def enviar_correo(destinatario: str, enlace: str) -> None:
    """Envía el enlace de verificación mediante Resend."""
    if not settings.resend_api_key or not settings.email_from:
        raise ErrorEnvioCorreo(
            "El proveedor de correo no está configurado"
        )

    contenido_html = f"""
    <h2>Bienvenido a NutriPlanner</h2>
    <p>Confirmá tu dirección de correo electrónico
    para activar tu cuenta.</p>
    <p>
        <a href="{escape(enlace, quote=True)}">
            Confirmar mi correo electrónico
        </a>
    </p>
    <p>Este enlace vence en
    {settings.email_verification_token_hours} horas.</p>
    <p>Si no solicitaste esta cuenta, ignorá el mensaje.</p>
    """

    try:
        respuesta = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": (
                    f"Bearer {settings.resend_api_key}"
                ),
                "Content-Type": "application/json",
            },
            json={
                "from": settings.email_from,
                "to": [destinatario],
                "subject": "Confirmá tu cuenta de NutriPlanner",
                "html": contenido_html,
            },
            timeout=10,
        )
        respuesta.raise_for_status()

    except httpx.HTTPError as error:
        raise ErrorEnvioCorreo(
            "No se pudo enviar el correo de confirmación"
        ) from error


def enviar_verificacion(
    db: Session,
    cuenta: Cuenta,
) -> bool:
    """
    Genera y envía un enlace de confirmación.
    Devuelve False si aún no puede reenviarse.
    """
    if cuenta.correo_verificado:
        return False

    ahora = ahora_utc()

    if cuenta.verificacion_enviada_en is not None:
        transcurrido = (
            ahora - normalizar_utc(
                cuenta.verificacion_enviada_en
            )
        ).total_seconds()

        if (
            transcurrido
            < settings.email_verification_resend_seconds
        ):
            return False

    # Guardar el estado anterior por si falla el envío.
    token_anterior = (
        cuenta.verificacion_token_hash,
        cuenta.verificacion_expira_en,
        cuenta.verificacion_enviada_en,
    )

    token = generar_token()

    enlace = (
        settings.frontend_url.rstrip("/")
        + "/verificar-correo?token="
        + quote(token, safe="")
    )

    # Guardamos únicamente el hash del token.
    cuenta.verificacion_token_hash = obtener_hash_token(
        token
    )
    cuenta.verificacion_expira_en = ahora + timedelta(
        hours=settings.email_verification_token_hours
    )
    cuenta.verificacion_enviada_en = ahora

    db.add(cuenta)
    db.commit()

    try:
        enviar_correo(cuenta.correo, enlace)

    except ErrorEnvioCorreo:
        # Restaurar el token anterior si el correo no pudo enviarse.
        (
            cuenta.verificacion_token_hash,
            cuenta.verificacion_expira_en,
            cuenta.verificacion_enviada_en,
        ) = token_anterior

        db.add(cuenta)
        db.commit()

        raise

    return True


def confirmar_verificacion(
    db: Session,
    token: str,
) -> bool:
    """Confirma el correo con un token válido y vigente."""

    hash_recibido = obtener_hash_token(token)

    cuenta = db.scalar(
        select(Cuenta).where(
            Cuenta.verificacion_token_hash
            == hash_recibido
        )
    )

    if cuenta is None:
        return False

    if cuenta.correo_verificado:
        return False

    if cuenta.verificacion_expira_en is None:
        return False

    if (
        normalizar_utc(cuenta.verificacion_expira_en)
        <= ahora_utc()
    ):
        return False

    cuenta.correo_verificado = True

    # Invalidamos el token para impedir reutilizarlo.
    cuenta.verificacion_token_hash = None
    cuenta.verificacion_expira_en = None

    db.add(cuenta)
    db.commit()

    return True
