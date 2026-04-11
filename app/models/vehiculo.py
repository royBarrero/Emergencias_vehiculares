from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id_vehiculo = Column(Integer, primary_key=True, index=True)
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"))
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    anio = Column(Integer)
    placa = Column(String(20), unique=True, nullable=False)
    color = Column(String(30))
    tipo_vehiculo = Column(String(30))

    conductor = relationship("Conductor", back_populates="vehiculos")