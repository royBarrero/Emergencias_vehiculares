from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class EstadoPagoEnum(str, enum.Enum):
    pendiente = "pendiente"
    completado = "completado"

class MetodoPagoEnum(str, enum.Enum):
    efectivo = "efectivo"
    qr = "qr"

class Pago(Base):
    __tablename__ = "pagos"

    id_pago = Column(Integer, primary_key=True, index=True)
    id_emergencia = Column(Integer, ForeignKey("emergencias.id_emergencia"), nullable=False, unique=True)
    monto_total = Column(Float, nullable=False)
    comision = Column(Float, nullable=False)
    monto_neto = Column(Float, nullable=False)
    metodo_pago = Column(Enum(MetodoPagoEnum), nullable=False)
    estado = Column(Enum(EstadoPagoEnum), default=EstadoPagoEnum.completado)
    created_at = Column(DateTime, default=datetime.utcnow)

    emergencia = relationship("Emergencia", backref="pago")