from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Conductor(Base):
    __tablename__ = "conductores"

    id_conductor = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), unique=True)
    licencia = Column(String(50))
    direccion = Column(String(200))

    usuario = relationship("Usuario", back_populates="conductor")
    vehiculos = relationship("Vehiculo", back_populates="conductor")
     # <-emergencias = relationship("Emergencia", back_populates="conductor")