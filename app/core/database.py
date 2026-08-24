"""Configuración del motor de base de datos SQLite con modo WAL.

Sigue las reglas de GEMINI.md §6.1: WAL activado, timeout de conexión
y sesiones gestionadas por SQLAlchemy.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 15},
)


@event.listens_for(engine, "connect")
def configurar_sqlite_pragma(dbapi_connection, connection_record):
    """Activa modo WAL y sincronización NORMAL para mejor rendimiento."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM."""
    pass


def obtener_sesion():
    """Generador de sesiones para inyección de dependencias de FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
