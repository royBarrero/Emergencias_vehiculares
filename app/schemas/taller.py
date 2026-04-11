from pydantic import BaseModel, EmailStr
from typing import Optional, List

class ServicioCrear(BaseModel):
    nombre_servicio: str
    descripcion: Optional[str] = None
    disponible: Optional[bool] = True

class ServicioRespuesta(BaseModel):
    id_servicio: int
    nombre_servicio: str
    descripcion: Optional[str] = None
    disponible: bool

    class Config:
        from_attributes = True

class TallerCrear(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str
    telefono: Optional[str] = None
    nombre_taller: str
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    descripcion: Optional[str] = None
    servicios: Optional[List[ServicioCrear]] = []

class TallerActualizar(BaseModel):
    nombre_taller: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    telefono: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None

class TallerRespuesta(BaseModel):
    id_taller: int
    nombre_taller: str
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    telefono: Optional[str] = None
    descripcion: Optional[str] = None
    estado: str
    calificacion_promedio: float
    nombre: str
    correo: str
    servicios: List[ServicioRespuesta] = []

    class Config:
        from_attributes = True