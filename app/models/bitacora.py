from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Session, relationship
from app.database import Base
from datetime import datetime, timezone, timedelta

class Bitacora(Base):
    __tablename__ = "bitacora"

    id_bitacora = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_tenant = Column(Integer, ForeignKey("tenants.id_tenant"), nullable=True)
    accion = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None))

    usuario = relationship("Usuario")
    tenant = relationship("Tenant")

