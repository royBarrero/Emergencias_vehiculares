from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class RecuperacionContrasena(Base):
    __tablename__ = "recuperacion_contrasena"

    id_recuperacion = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    token = Column(String(255), nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    usado = Column(Boolean, default=False)

    usuario = relationship("Usuario")