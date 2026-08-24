"""Esquemas Pydantic para validación de notificaciones entrantes y salientes."""

from pydantic import BaseModel, Field


class NotificacionEntrada(BaseModel):
    """Payload de entrada para crear una notificación.

    Campos:
        source: origen de la notificación (ej. "monitoring", "mi-app").
        title: título breve del evento.
        message: cuerpo del mensaje (máximo 4000 caracteres).
        severity: nivel de severidad (info, warning, critical, success).
    """

    source: str = Field(
        ..., min_length=1, max_length=100,
        description="Origen de la notificación",
    )
    title: str = Field(
        ..., min_length=1, max_length=200,
        description="Título de la notificación",
    )
    message: str = Field(
        ..., min_length=1, max_length=4000,
        description="Cuerpo del mensaje",
    )
    severity: str = Field(
        default="info", max_length=20,
        description="Nivel: info, warning, critical, success",
    )


class NotificacionRespuesta(BaseModel):
    """Respuesta devuelta tras crear una notificación."""

    status: str
    id: int

    model_config = {"from_attributes": True}
