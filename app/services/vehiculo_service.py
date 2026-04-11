from sqlalchemy.orm import Session
from app.models.vehiculo import Vehiculo

def crear_vehiculo(db: Session, datos):
    existe = db.query(Vehiculo).filter(Vehiculo.placa == datos.placa).first()
    if existe:
        return None

    nuevo = Vehiculo(
        id_conductor=datos.id_conductor,
        marca=datos.marca,
        modelo=datos.modelo,
        anio=datos.anio,
        placa=datos.placa,
        color=datos.color,
        tipo_vehiculo=datos.tipo_vehiculo
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def obtener_vehiculos_conductor(db: Session, id_conductor: int):
    return db.query(Vehiculo).filter(Vehiculo.id_conductor == id_conductor).all()

def obtener_vehiculo(db: Session, id_vehiculo: int):
    return db.query(Vehiculo).filter(Vehiculo.id_vehiculo == id_vehiculo).first()

def actualizar_vehiculo(db: Session, id_vehiculo: int, datos):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == id_vehiculo).first()
    if not vehiculo:
        return None

    if datos.marca: vehiculo.marca = datos.marca
    if datos.modelo: vehiculo.modelo = datos.modelo
    if datos.anio: vehiculo.anio = datos.anio
    if datos.color: vehiculo.color = datos.color
    if datos.tipo_vehiculo: vehiculo.tipo_vehiculo = datos.tipo_vehiculo

    db.commit()
    db.refresh(vehiculo)
    return vehiculo

def eliminar_vehiculo(db: Session, id_vehiculo: int):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == id_vehiculo).first()
    if not vehiculo:
        return False
    db.delete(vehiculo)
    db.commit()
    return True