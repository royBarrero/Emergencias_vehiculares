from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.conductor import ConductorCrear, ConductorActualizar, ConductorRespuesta
from app.services.conductor_service import crear_conductor, obtener_conductor, actualizar_conductor
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from typing import List

router = APIRouter(
    prefix="/conductores",
    tags=["Conductores"]
)

@router.post("/", response_model=ConductorRespuesta)
def registrar_conductor(datos: ConductorCrear, db: Session = Depends(get_db)):
    conductor = crear_conductor(db, datos)
    if not conductor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )
    return {
        "id_conductor": conductor.id_conductor,
        "licencia": conductor.licencia,
        "direccion": conductor.direccion,
        "nombre": conductor.usuario.nombre,
        "correo": conductor.usuario.correo,
        "telefono": conductor.usuario.telefono
    }

@router.get("/{id_conductor}", response_model=ConductorRespuesta)
def ver_conductor(id_conductor: int, db: Session = Depends(get_db)):
    conductor = obtener_conductor(db, id_conductor)
    if not conductor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    return {
        "id_conductor": conductor.id_conductor,
        "licencia": conductor.licencia,
        "direccion": conductor.direccion,
        "nombre": conductor.usuario.nombre,
        "correo": conductor.usuario.correo,
        "telefono": conductor.usuario.telefono
    }

@router.put("/{id_conductor}", response_model=ConductorRespuesta)
def actualizar_conductor_endpoint(id_conductor: int, datos: ConductorActualizar, db: Session = Depends(get_db)):
    conductor = actualizar_conductor(db, id_conductor, datos)
    if not conductor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    return {
        "id_conductor": conductor.id_conductor,
        "licencia": conductor.licencia,
        "direccion": conductor.direccion,
        "nombre": conductor.usuario.nombre,
        "correo": conductor.usuario.correo,
        "telefono": conductor.usuario.telefono
    }
@router.get("/", response_model=List[ConductorRespuesta])
def listar_conductores(db: Session = Depends(get_db)):
    conductores = db.query(Conductor).all()
    return [{
        "id_conductor": c.id_conductor,
        "licencia": c.licencia,
        "direccion": c.direccion,
        "nombre": c.usuario.nombre,
        "correo": c.usuario.correo,
        "telefono": c.usuario.telefono
    } for c in conductores]

@router.delete("/{id_conductor}")
def eliminar_conductor(id_conductor: int, db: Session = Depends(get_db)):
    conductor = db.query(Conductor).filter(
        Conductor.id_conductor == id_conductor
    ).first()
    if not conductor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    # Eliminar usuario asociado
    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == conductor.id_usuario
    ).first()
    db.delete(conductor)
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Conductor eliminado correctamente"}