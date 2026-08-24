"""Fixtures y configuración para los tests.

Las variables de entorno se establecen ANTES de importar la aplicación
para que Pydantic Settings las recoja correctamente.
"""

import os

# Configurar variables de entorno ficticias para los tests
os.environ["TELEGRAM_BOT_TOKEN"] = "token-falso-para-tests"
os.environ["TELEGRAM_CHAT_ID"] = "123456789"
os.environ["NOTIFICATION_API_KEY"] = "clave-test"
os.environ["DATABASE_URL"] = "sqlite:///data/test.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Cliente HTTP de prueba con ciclo de vida completo de la app."""
    with TestClient(app) as c:
        yield c
