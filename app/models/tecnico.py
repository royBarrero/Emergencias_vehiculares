from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Tecnico(Base):
    __tablename__ = "tecnicos"

    id_tecnico = Column(Integer, primary_key=True, index=True)
    id_taller = Column(Integer, ForeignKey("talleres.id_taller"))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), unique=True)
    especialidad = Column(String(100))
    estado_disponibilidad = Column(String(20), default="disponible")
    latitud_actual = Column(Float)
    longitud_actual = Column(Float)

    taller = relationship("Taller", back_populates="tecnicos")
    usuario = relationship("Usuario")