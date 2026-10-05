"""Formateador de notificaciones para Telegram.

Separa la lógica de presentación de la lógica HTTP, facilitando
cambios visuales sin modificar los endpoints.
"""

import html

from app.schemas.notification import NotificacionEntrada

# Mapa de iconos según la severidad de la notificación
_ICONOS_SEVERIDAD: dict[str, str] = {
    "info": "🔵",
    "warning": "🟠",
    "critical": "🔴",
    "success": "🟢",
}


def formatear_notificacion(notificacion: NotificacionEntrada) -> str:
    """Convierte una notificación en texto HTML para Telegram.

    Ejemplo de salida:
        🔴 <b>Servidor caído</b>

        <b>Origen:</b> monitoring
        <b>Nivel:</b> critical

        El servidor web no responde.
    """
    icono = _ICONOS_SEVERIDAD.get(notificacion.severity, "🔔")
    titulo_escapado = html.escape(notificacion.title, quote=False)
    origen_escapado = html.escape(notificacion.source, quote=False)
    severidad_escapada = html.escape(notificacion.severity, quote=False)
    mensaje_escapado = html.escape(notificacion.message, quote=False)

    return (
        f"{icono} <b>{titulo_escapado}</b>\n\n"
        f"<b>Origen:</b> {origen_escapado}\n"
        f"<b>Nivel:</b> {severidad_escapada}\n\n"
        f"{mensaje_escapado}"
    )
