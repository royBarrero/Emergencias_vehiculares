from app.models import rol 
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.usuario import UsuarioCrear, LoginRequest, TokenRespuesta, UsuarioRespuesta
from app.services.auth_service import autenticar_usuario, registrar_usuario, crear_token
from jose import JWTError, jwt
from app.config import SECRET_KEY, ALGORITHM
from app.models.usuario import Usuario
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.bitacora_service import registrar_evento

security = HTTPBearer()
router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post("/login", response_model=TokenRespuesta)
def login(request: Request, datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, datos.correo, datos.contrasena)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )
    
    # Obtener tenant_id si el usuario es dueño de un taller
    tenant_id = None
    if usuario.id_rol == 2:
        from app.models.taller import Taller
        taller = db.query(Taller).filter(Taller.id_usuario == usuario.id_usuario).first()
        if taller:
            tenant_id = taller.id_tenant
    elif usuario.id_rol == 3:
        from app.models.tecnico import Tecnico
        from app.models.taller import Taller
        tecnico = db.query(Tecnico).filter(Tecnico.id_usuario == usuario.id_usuario).first()
        if tecnico:
            taller = db.query(Taller).filter(Taller.id_taller == tecnico.id_taller).first()
            if taller:
                tenant_id = taller.id_tenant
    elif usuario.id_rol == 5:
        from app.models.tenant import Tenant
        tenant = db.query(Tenant).filter(Tenant.id_usuario_admin == usuario.id_usuario).first()
        if tenant:
            tenant_id = tenant.id_tenant

    token = crear_token({"sub": str(usuario.id_usuario), "rol": usuario.id_rol, "tenant_id": tenant_id})
    # Registrar en bitácora
    registrar_evento(
        db,
        id_usuario=usuario.id_usuario,
        accion="LOGIN",
        descripcion=f"Inicio de sesión exitoso",
        ip_address=request.client.host if hasattr(request, 'client') else None,
        id_tenant=tenant_id
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "id_rol": usuario.id_rol,
        "tenant_id": tenant_id
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
    # Registrar en bitácora
    registrar_evento(
        db,
        id_usuario=nuevo.id_usuario,
        accion="REGISTRO",
        descripcion=f"Nuevo usuario registrado",
        ip_address=usuario.ip_address if hasattr(usuario, 'ip_address') else None
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
    
    # Agregar tenant_id al objeto usuario desde el token
    usuario.tenant_id = payload.get("tenant_id")
    return usuario