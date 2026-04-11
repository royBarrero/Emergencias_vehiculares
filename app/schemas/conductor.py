from pydantic import BaseModel, EmailStr
from typing import Optional

class ConductorCrear(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str
    telefono: Optional[str] = None
    licencia: Optional[str] = None
    direccion: Optional[str] = None

class ConductorActualizar(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    licencia: Optional[str] = None
    direccion: Optional[str] = None

class ConductorRespuesta(BaseModel):
    id_conductor: int
    licencia: Optional[str] = None
    direccion: Optional[str] = None
    nombre: str
    correo: str
    telefono: Optional[str] = None

    class Config:
        from_attributes = True