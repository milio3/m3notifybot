"""Modelo ORM para la tabla de notificaciones."""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class NotificacionDB(Base):
    """Registro persistente de cada notificación recibida y su estado de entrega."""

    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, default="info")
    entregada = Column(Boolean, nullable=False, default=False)
    error = Column(Text, nullable=True)
    creada_en = Column(DateTime, nullable=False, server_default=func.now())
