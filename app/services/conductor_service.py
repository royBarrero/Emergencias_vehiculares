from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from app.services.auth_service import encriptar_contrasena

def crear_conductor(db: Session, datos):
    # Verificar si el correo ya existe
    existe = db.query(Usuario).filter(Usuario.correo == datos.correo).first()
    if existe:
        return None

    # Crear usuario
    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        contrasena=encriptar_contrasena(datos.contrasena),
        telefono=datos.telefono,
        id_rol=1  # rol conductor
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # Crear conductor
    nuevo_conductor = Conductor(
        id_usuario=nuevo_usuario.id_usuario,
        licencia=datos.licencia,
        direccion=datos.direccion
    )
    db.add(nuevo_conductor)
    db.commit()
    db.refresh(nuevo_conductor)
    return nuevo_conductor

def obtener_conductor(db: Session, id_conductor: int):
    return db.query(Conductor).filter(Conductor.id_conductor == id_conductor).first()

def actualizar_conductor(db: Session, id_conductor: int, datos):
    conductor = db.query(Conductor).filter(Conductor.id_conductor == id_conductor).first()
    if not conductor:
        return None

    # Actualizar datos del usuario
    if datos.nombre:
        conductor.usuario.nombre = datos.nombre
    if datos.telefono:
        conductor.usuario.telefono = datos.telefono

    # Actualizar datos del conductor
    if datos.licencia:
        conductor.licencia = datos.licencia
    if datos.direccion:
        conductor.direccion = datos.direccion

    db.commit()
    db.refresh(conductor)
    return conductor