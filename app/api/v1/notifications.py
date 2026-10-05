"""Endpoint de recepción de notificaciones.

Recibe notificaciones vía HTTP, las persiste en SQLite y las envía
al chat de Telegram configurado.
"""

import logging
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import obtener_sesion
from app.models.notification import NotificacionDB
from app.schemas.notification import NotificacionEntrada, NotificacionRespuesta
from app.services.telegram import TelegramError, enviar_notificacion

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Notificaciones"])


@router.post(
    "/notifications",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=NotificacionRespuesta,
)
async def crear_notificacion(
    notificacion: NotificacionEntrada,
    x_api_key: str = Header(..., description="Clave API de autenticación"),
    db: Session = Depends(obtener_sesion),
):
    """Recibe una notificación, la persiste en la BD y la envía a Telegram.

    - 202: notificación aceptada y entregada.
    - 401: clave API inválida.
    - 422: payload no válido.
    - 502: error al comunicarse con Telegram.
    """
    # Autenticación segura por API key contra timing attacks
    if not secrets.compare_digest(x_api_key, settings.NOTIFICATION_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave API inválida",
        )

    # Persistir la notificación en la base de datos
    registro = NotificacionDB(
        source=notificacion.source,
        title=notificacion.title,
        message=notificacion.message,
        severity=notificacion.severity,
    )
    db.add(registro)
    db.flush()  # Genera el ID autoincremental sin commit anticipado a disco

    logger.info(
        "Notificación recibida id=%s origen=%s severidad=%s",
        registro.id,
        registro.source,
        registro.severity,
    )

    # Enviar a Telegram
    try:
        await enviar_notificacion(notificacion)
        registro.entregada = True
        db.commit()
    except TelegramError as e:
        registro.error = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo entregar la notificación a Telegram",
        )

    return NotificacionRespuesta(status="accepted", id=registro.id)
