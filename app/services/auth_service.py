from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.models.usuario import Usuario
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encriptar_contrasena(contrasena: str) -> str:
    return pwd_context.hash(contrasena)

def verificar_contrasena(contrasena: str, hash: str) -> bool:
    return pwd_context.verify(contrasena, hash)

def crear_token(data: dict) -> str:
    datos = data.copy()
    expiracion = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    datos.update({"exp": expiracion})
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)

def autenticar_usuario(db: Session, correo: str, contrasena: str):
    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    if not usuario:
        return None
    if not verificar_contrasena(contrasena, usuario.contrasena):
        return None
    return usuario

def registrar_usuario(db: Session, nombre: str, correo: str, contrasena: str, telefono: str, id_rol: int):
    # Verificar si el correo ya existe
    existe = db.query(Usuario).filter(Usuario.correo == correo).first()
    if existe:
        return None
    
    nuevo_usuario = Usuario(
        nombre=nombre,
        correo=correo,
        contrasena=encriptar_contrasena(contrasena),
        telefono=telefono,
        id_rol=id_rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario