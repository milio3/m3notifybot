"""Endpoints de control de salud del servicio.

Implementa liveness (/health) y readiness (/ready) según GEMINI.md §5.2.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine

router = APIRouter(tags=["Salud"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Comprobación de vitalidad (liveness).

    Devuelve el estado del servicio y su versión.
    """
    return {"status": "ok", "version": settings.VERSION}


@router.get("/ready", status_code=status.HTTP_200_OK)
def ready_check():
    """Comprobación de disponibilidad (readiness).

    Verifica que la conexión a la base de datos funciona correctamente.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unready", "database_error": str(e)},
        )
