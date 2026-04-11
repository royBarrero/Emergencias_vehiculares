from sqlalchemy.orm import Session
from app.models.rol import Rol
from app.models.usuario import Usuario

def obtener_roles(db: Session):
    return db.query(Rol).all()

def obtener_rol(db: Session, id_rol: int):
    return db.query(Rol).filter(Rol.id_rol == id_rol).first()

def crear_rol(db: Session, datos):
    existe = db.query(Rol).filter(Rol.nombre == datos.nombre).first()
    if existe:
        return None

    nuevo_rol = Rol(
        nombre=datos.nombre,
        descripcion=datos.descripcion
    )
    db.add(nuevo_rol)
    db.commit()
    db.refresh(nuevo_rol)
    return nuevo_rol

def actualizar_rol(db: Session, id_rol: int, datos):
    rol = db.query(Rol).filter(Rol.id_rol == id_rol).first()
    if not rol:
        return None

    if datos.nombre: rol.nombre = datos.nombre
    if datos.descripcion: rol.descripcion = datos.descripcion

    db.commit()
    db.refresh(rol)
    return rol

def asignar_rol(db: Session, id_usuario: int, id_rol: int):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        return None

    rol = db.query(Rol).filter(Rol.id_rol == id_rol).first()
    if not rol:
        return None

    usuario.id_rol = id_rol
    db.commit()
    db.refresh(usuario)
    return usuario