"""Formateador de notificaciones para Telegram.

Separa la lógica de presentación de la lógica HTTP, facilitando
cambios visuales sin modificar los endpoints.
"""

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

    return (
        f"{icono} <b>{notificacion.title}</b>\n\n"
        f"<b>Origen:</b> {notificacion.source}\n"
        f"<b>Nivel:</b> {notificacion.severity}\n\n"
        f"{notificacion.message}"
    )
