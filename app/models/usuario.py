from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    telefono = Column(String(20))
    fecha_registro = Column(DateTime, default=datetime.now)
    estado = Column(Boolean, default=True)
    id_rol = Column(Integer, ForeignKey("roles.id_rol"))

    rol = relationship("Rol", back_populates="usuarios")
    conductor = relationship("Conductor", back_populates="usuario", uselist=False) 
    taller = relationship("Taller", back_populates="usuario", uselist=False)