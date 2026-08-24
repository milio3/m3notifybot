"""Punto de entrada de la aplicación m3notifybot.

Crea la instancia de FastAPI, registra los routers y configura
el ciclo de vida (lifespan) para inicializar la base de datos.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1.notifications import router as notifications_router
from app.core.config import settings
from app.core.database import Base, engine

# Configurar logging según el modo de depuración
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación.

    Al arrancar: crea las tablas de la BD si no existen.
    Al detenerse: registra el cierre.
    """
    logger.info("Iniciando %s v%s", settings.PROJECT_NAME, settings.VERSION)
    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos inicializada")
    yield
    logger.info("Deteniendo %s", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(notifications_router)
