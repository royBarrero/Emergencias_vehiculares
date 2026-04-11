from pydantic import BaseModel, EmailStr

class SolicitudRecuperacion(BaseModel):
    correo: EmailStr

class VerificarToken(BaseModel):
    token: str

class CambiarContrasena(BaseModel):
    token: str
    nueva_contrasena: str