from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class EstadoCotizacionEnum(str, enum.Enum):
    solicitada = "solicitada"
    enviada = "enviada"
    aceptada = "aceptada"
    rechazada = "rechazada"

class Cotizacion(Base):
    __tablename__ = "cotizaciones"

    id_cotizacion = Column(Integer, primary_key=True, index=True)
    id_emergencia = Column(Integer, ForeignKey("emergencias.id_emergencia"), nullable=False)
    id_taller = Column(Integer, ForeignKey("talleres.id_taller"), nullable=False)
    monto_estimado = Column(Float, nullable=True)
    descripcion_servicio = Column(Text, nullable=True)
    tiempo_estimado = Column(String(100), nullable=True)
    observacion = Column(Text, nullable=True)
    estado = Column(Enum(EstadoCotizacionEnum), default=EstadoCotizacionEnum.solicitada, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    emergencia = relationship("Emergencia", backref="cotizaciones")
    taller = relationship("Taller", backref="cotizaciones")