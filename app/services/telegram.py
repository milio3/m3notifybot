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


_http_client: httpx.AsyncClient | None = None


def obtener_cliente_http() -> httpx.AsyncClient:
    """Obtiene o inicializa el cliente HTTP reutilizable con connection pooling."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS)
    return _http_client


async def cerrar_cliente_http() -> None:
    """Cierra las conexiones del cliente HTTP persistente al detener el servicio."""
    global _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None


class TelegramError(Exception):
    """Error al comunicarse con la API de Telegram."""
    pass


async def enviar_notificacion(
    notificacion: NotificacionEntrada,
    client: httpx.AsyncClient | None = None,
) -> None:
    """Envía una notificación formateada al chat de Telegram configurado.

    Lanza TelegramError si la API de Telegram responde con error o ante fallos de red.
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

    http_client = client or obtener_cliente_http()

    try:
        response = await http_client.post(url, json=payload)
    except httpx.RequestError as exc:
        logger.error("Error de conexión al comunicar con Telegram: %s", exc)
        raise TelegramError(
            f"Fallo de red o timeout al comunicar con Telegram: {exc}"
        ) from exc

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
