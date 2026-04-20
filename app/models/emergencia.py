from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class PrioridadEnum(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"

class EstadoEmergenciaEnum(str, enum.Enum):
    pendiente = "pendiente"
    buscando_taller = "buscando_taller"
    asignada = "asignada"
    en_camino = "en_camino"
    atendiendo = "atendiendo"
    finalizada = "finalizada"
    cancelada = "cancelada"

class TipoEvidenciaEnum(str, enum.Enum):
    foto = "foto"
    audio = "audio"

class Emergencia(Base):
    __tablename__ = "emergencias"

    id_emergencia = Column(Integer, primary_key=True, index=True)
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"), nullable=False)
    id_vehiculo = Column(Integer, ForeignKey("vehiculos.id_vehiculo"), nullable=False)

    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    direccion_aproximada = Column(String(500), nullable=True)

    tipo_incidente = Column(String(100), nullable=False)
    prioridad = Column(Enum(PrioridadEnum), default=PrioridadEnum.media, nullable=False)
    descripcion = Column(Text, nullable=True)

    transcripcion_audio = Column(Text, nullable=True)

    estado = Column(Enum(EstadoEmergenciaEnum), default=EstadoEmergenciaEnum.pendiente, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    evidencias = relationship("EvidenciaEmergencia", back_populates="emergencia", cascade="all, delete-orphan")

class EvidenciaEmergencia(Base):
    __tablename__ = "evidencias_emergencia"

    id_evidencia = Column(Integer, primary_key=True, index=True)
    id_emergencia = Column(Integer, ForeignKey("emergencias.id_emergencia"), nullable=False)
    tipo = Column(Enum(TipoEvidenciaEnum), nullable=False)
    url_archivo = Column(String(1000), nullable=False)
    descripcion = Column(String(255), nullable=True)
    transcripcion = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    emergencia = relationship("Emergencia", back_populates="evidencias")