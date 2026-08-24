"""Cliente asíncrono para la API de Telegram Bot.

Envía notificaciones formateadas al chat configurado usando httpx
con timeout explícito (GEMINI.md §5.3).
"""

import logging

import httpx

from app.core.config import settings
from app.schemas.notification import NotificacionEntrada
from app.utils.formatter import formatear_notificacion

logger = logging.getLogger(__name__)


class TelegramError(Exception):
    """Error al comunicarse con la API de Telegram."""
    pass


async def enviar_notificacion(notificacion: NotificacionEntrada) -> None:
    """Envía una notificación formateada al chat de Telegram configurado.

    Lanza TelegramError si la API de Telegram responde con error.
    """
    url = (
        f"https://api.telegram.org/"
        f"bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    texto = formatear_notificacion(notificacion)

    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
    }

    async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
        response = await client.post(url, json=payload)

    if response.is_error:
        logger.error(
            "Error al enviar a Telegram: %s %s",
            response.status_code,
            response.text,
        )
        raise TelegramError(
            f"Error en la API de Telegram: {response.status_code}"
        )

    logger.info(
        "Notificación enviada a Telegram — origen=%s severidad=%s",
        notificacion.source,
        notificacion.severity,
    )
