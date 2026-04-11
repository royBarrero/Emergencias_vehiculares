from pydantic import BaseModel
from typing import Optional

class RolCrear(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class RolActualizar(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class RolRespuesta(BaseModel):
    id_rol: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True

class AsignarRol(BaseModel):
    id_usuario: int
    id_rol: int