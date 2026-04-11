from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.tecnico import Tecnico
from app.services.auth_service import encriptar_contrasena

def crear_tecnico(db: Session, datos):
    existe = db.query(Usuario).filter(Usuario.correo == datos.correo).first()
    if existe:
        return None

    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        contrasena=encriptar_contrasena(datos.contrasena),
        telefono=datos.telefono,
        id_rol=3  # rol tecnico
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    nuevo_tecnico = Tecnico(
        id_taller=datos.id_taller,
        id_usuario=nuevo_usuario.id_usuario,
        especialidad=datos.especialidad
    )
    db.add(nuevo_tecnico)
    db.commit()
    db.refresh(nuevo_tecnico)
    return nuevo_tecnico

def obtener_tecnicos_taller(db: Session, id_taller: int):
    return db.query(Tecnico).filter(Tecnico.id_taller == id_taller).all()

def obtener_tecnico(db: Session, id_tecnico: int):
    return db.query(Tecnico).filter(Tecnico.id_tecnico == id_tecnico).first()

def actualizar_tecnico(db: Session, id_tecnico: int, datos):
    tecnico = db.query(Tecnico).filter(Tecnico.id_tecnico == id_tecnico).first()
    if not tecnico:
        return None

    if datos.nombre: tecnico.usuario.nombre = datos.nombre
    if datos.telefono: tecnico.usuario.telefono = datos.telefono
    if datos.especialidad: tecnico.especialidad = datos.especialidad

    db.commit()
    db.refresh(tecnico)
    return tecnico

def cambiar_disponibilidad(db: Session, id_tecnico: int, estado: str):
    tecnico = db.query(Tecnico).filter(Tecnico.id_tecnico == id_tecnico).first()
    if not tecnico:
        return None

    tecnico.estado_disponibilidad = estado
    db.commit()
    db.refresh(tecnico)
    return tecnico