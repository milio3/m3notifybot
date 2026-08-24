"""Tests para el endpoint de notificaciones POST /api/v1/notifications."""

from unittest.mock import AsyncMock, patch

# Payload válido de ejemplo
NOTIFICACION_VALIDA = {
    "source": "test",
    "title": "Título de prueba",
    "message": "Mensaje de prueba para verificar el endpoint.",
    "severity": "info",
}

CABECERAS_VALIDAS = {"X-API-Key": "clave-test"}
CABECERAS_INVALIDAS = {"X-API-Key": "clave-incorrecta"}


def test_api_key_incorrecta_retorna_401(client):
    """Una API key incorrecta debe devolver 401 Unauthorized."""
    respuesta = client.post(
        "/api/v1/notifications",
        json=NOTIFICACION_VALIDA,
        headers=CABECERAS_INVALIDAS,
    )
    assert respuesta.status_code == 401


def test_payload_invalido_retorna_422(client):
    """Un payload sin campos obligatorios debe devolver 422."""
    respuesta = client.post(
        "/api/v1/notifications",
        json={"source": "test"},  # Faltan title y message
        headers=CABECERAS_VALIDAS,
    )
    assert respuesta.status_code == 422


@patch(
    "app.api.v1.notifications.enviar_notificacion",
    new_callable=AsyncMock,
)
def test_notificacion_correcta_retorna_202(mock_telegram, client):
    """Una notificación válida con Telegram OK debe devolver 202 Accepted."""
    mock_telegram.return_value = None

    respuesta = client.post(
        "/api/v1/notifications",
        json=NOTIFICACION_VALIDA,
        headers=CABECERAS_VALIDAS,
    )
    assert respuesta.status_code == 202
    datos = respuesta.json()
    assert datos["status"] == "accepted"
    assert "id" in datos

    mock_telegram.assert_called_once()


@patch(
    "app.api.v1.notifications.enviar_notificacion",
    new_callable=AsyncMock,
)
def test_telegram_caido_retorna_502(mock_telegram, client):
    """Si Telegram falla, debe devolver 502 Bad Gateway."""
    from app.services.telegram import TelegramError

    mock_telegram.side_effect = TelegramError("Error simulado")

    respuesta = client.post(
        "/api/v1/notifications",
        json=NOTIFICACION_VALIDA,
        headers=CABECERAS_VALIDAS,
    )
    assert respuesta.status_code == 502
