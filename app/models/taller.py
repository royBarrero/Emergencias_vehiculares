from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Taller(Base):
    __tablename__ = "talleres"

    id_taller = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), unique=True)
    nombre_taller = Column(String(100), nullable=False)
    direccion = Column(String(200))
    latitud = Column(Float)
    longitud = Column(Float)
    telefono = Column(String(20))
    descripcion = Column(String(500))
    estado = Column(String(20), default="pendiente")
    calificacion_promedio = Column(Float, default=0.0)

    usuario = relationship("Usuario", back_populates="taller")
    servicios = relationship("ServicioTaller", back_populates="taller")
    tecnicos = relationship("Tecnico", back_populates="taller")