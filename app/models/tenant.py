from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Tenant(Base):
    __tablename__ = "tenants"

    id_tenant = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    estado = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    id_usuario_admin = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)

    talleres = relationship("Taller", back_populates="tenant")
    admin = relationship("Usuario", foreign_keys=[id_usuario_admin])