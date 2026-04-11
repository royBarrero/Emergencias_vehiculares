from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: Optional[str] = None
    id_rol: int

class UsuarioCrear(UsuarioBase):
    contrasena: str

class UsuarioRespuesta(UsuarioBase):
    id_usuario: int
    fecha_registro: datetime
    estado: bool

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str

class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str
    id_usuario: int
    nombre: str
    id_rol: int