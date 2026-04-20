from app.models import rol 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.usuario import UsuarioCrear, LoginRequest, TokenRespuesta, UsuarioRespuesta
from app.services.auth_service import autenticar_usuario, registrar_usuario, crear_token
from jose import JWTError, jwt
from app.config import SECRET_KEY, ALGORITHM
from app.models.usuario import Usuario
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: str = payload.get("sub")
        if id_usuario is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    usuario = db.query(Usuario).filter(Usuario.id_usuario == int(id_usuario)).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario