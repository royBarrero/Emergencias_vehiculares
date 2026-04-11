from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ServicioTaller(Base):
    __tablename__ = "servicios_taller"

    id_servicio = Column(Integer, primary_key=True, index=True)
    id_taller = Column(Integer, ForeignKey("talleres.id_taller"))
    nombre_servicio = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    disponible = Column(Boolean, default=True)

    taller = relationship("Taller", back_populates="servicios")