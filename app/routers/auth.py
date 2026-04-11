from app.models import rol 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.usuario import UsuarioCrear, LoginRequest, TokenRespuesta, UsuarioRespuesta
from app.services.auth_service import autenticar_usuario, registrar_usuario, crear_token

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post("/login", response_model=TokenRespuesta)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, request.correo, request.contrasena)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )
    token = crear_token({"sub": str(usuario.id_usuario), "rol": usuario.id_rol})
    return {
        "access_token": token,
        "token_type": "bearer",
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "id_rol": usuario.id_rol
    }

@router.post("/registro", response_model=UsuarioRespuesta)
def registro(usuario: UsuarioCrear, db: Session = Depends(get_db)):
    nuevo = registrar_usuario(
        db,
        usuario.nombre,
        usuario.correo,
        usuario.contrasena,
        usuario.telefono,
        usuario.id_rol
    )
    if not nuevo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )
    return nuevo