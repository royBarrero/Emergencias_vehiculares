from pydantic import BaseModel, EmailStr
from typing import Optional

class TecnicoCrear(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str
    telefono: Optional[str] = None
    id_taller: int
    especialidad: Optional[str] = None

class TecnicoActualizar(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    especialidad: Optional[str] = None

class CambiarDisponibilidad(BaseModel):
    estado_disponibilidad: str  # disponible, ocupado, inactivo

class TecnicoRespuesta(BaseModel):
    id_tecnico: int
    id_taller: int
    especialidad: Optional[str] = None
    estado_disponibilidad: str
    latitud_actual: Optional[float] = None
    longitud_actual: Optional[float] = None
    nombre: str
    correo: str
    telefono: Optional[str] = None
    nombre_taller: Optional[str] = None

    class Config:
        from_attributes = True