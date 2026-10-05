"""Configuración centralizada de la aplicación m3notifybot.

Todas las variables se cargan desde el entorno o desde el fichero .env.
"""

from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parámetros de configuración de la aplicación."""

    # Metadatos del proyecto
    PROJECT_NAME: str = "m3notifybot"
    VERSION: ClassVar[str] = "0.1.2"
    DEBUG: bool = False

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: int

    # Autenticación de peticiones entrantes
    NOTIFICATION_API_KEY: str

    # Base de datos SQLite
    DATABASE_URL: str = "sqlite:///data/database.db"

    # Timeout para peticiones HTTP salientes (segundos)
    HTTP_TIMEOUT_SECONDS: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
