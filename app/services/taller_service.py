from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.taller import Taller
from app.models.servicio_taller import ServicioTaller
from app.services.auth_service import encriptar_contrasena

def crear_taller(db: Session, datos):
    existe = db.query(Usuario).filter(Usuario.correo == datos.correo).first()
    if existe:
        return None

    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        contrasena=encriptar_contrasena(datos.contrasena),
        telefono=datos.telefono,
        id_rol=2  # rol taller
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    nuevo_taller = Taller(
        id_usuario=nuevo_usuario.id_usuario,
        nombre_taller=datos.nombre_taller,
        direccion=datos.direccion,
        latitud=datos.latitud,
        longitud=datos.longitud,
        descripcion=datos.descripcion,
        telefono=datos.telefono
    )
    db.add(nuevo_taller)
    db.commit()
    db.refresh(nuevo_taller)

    # Agregar servicios si vienen
    for servicio in datos.servicios:
        nuevo_servicio = ServicioTaller(
            id_taller=nuevo_taller.id_taller,
            nombre_servicio=servicio.nombre_servicio,
            descripcion=servicio.descripcion,
            disponible=servicio.disponible
        )
        db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_taller)
    return nuevo_taller

def obtener_taller(db: Session, id_taller: int):
    return db.query(Taller).filter(Taller.id_taller == id_taller).first()

def obtener_todos_talleres(db: Session):
    return db.query(Taller).all()

def actualizar_taller(db: Session, id_taller: int, datos):
    taller = db.query(Taller).filter(Taller.id_taller == id_taller).first()
    if not taller:
        return None

    if datos.nombre_taller: taller.nombre_taller = datos.nombre_taller
    if datos.direccion: taller.direccion = datos.direccion
    if datos.latitud: taller.latitud = datos.latitud
    if datos.longitud: taller.longitud = datos.longitud
    if datos.telefono: taller.telefono = datos.telefono
    if datos.descripcion: taller.descripcion = datos.descripcion
    if datos.estado: taller.estado = datos.estado

    db.commit()
    db.refresh(taller)
    return taller

def agregar_servicio(db: Session, id_taller: int, datos):
    taller = db.query(Taller).filter(Taller.id_taller == id_taller).first()
    if not taller:
        return None

    nuevo_servicio = ServicioTaller(
        id_taller=id_taller,
        nombre_servicio=datos.nombre_servicio,
        descripcion=datos.descripcion,
        disponible=datos.disponible
    )
    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)
    return nuevo_servicio