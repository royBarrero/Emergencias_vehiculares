from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.tecnico import TecnicoCrear, TecnicoActualizar, CambiarDisponibilidad, TecnicoRespuesta
from app.services.tecnico_service import (
    crear_tecnico, obtener_tecnicos_taller,
    obtener_tecnico, actualizar_tecnico, cambiar_disponibilidad
)
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
router = APIRouter(
    prefix="/tecnicos",
    tags=["Técnicos"]
)

@router.post("/", response_model=TecnicoRespuesta)
def registrar_tecnico(datos: TecnicoCrear, db: Session = Depends(get_db)):
    tecnico = crear_tecnico(db, datos)
    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )
    return {
        "id_tecnico": tecnico.id_tecnico,
        "id_taller": tecnico.id_taller,
        "especialidad": tecnico.especialidad,
        "estado_disponibilidad": tecnico.estado_disponibilidad,
        "latitud_actual": tecnico.latitud_actual,
        "longitud_actual": tecnico.longitud_actual,
        "nombre": tecnico.usuario.nombre,
        "correo": tecnico.usuario.correo,
        "telefono": tecnico.usuario.telefono
    }

@router.get("/taller/{id_taller}", response_model=List[TecnicoRespuesta])
def listar_tecnicos(id_taller: int, db: Session = Depends(get_db)):
    tecnicos = obtener_tecnicos_taller(db, id_taller)
    return [{
        "id_tecnico": t.id_tecnico,
        "id_taller": t.id_taller,
        "especialidad": t.especialidad,
        "estado_disponibilidad": t.estado_disponibilidad,
        "latitud_actual": t.latitud_actual,
        "longitud_actual": t.longitud_actual,
        "nombre": t.usuario.nombre,
        "correo": t.usuario.correo,
        "telefono": t.usuario.telefono
    } for t in tecnicos]

@router.get("/{id_tecnico}", response_model=TecnicoRespuesta)
def ver_tecnico(id_tecnico: int, db: Session = Depends(get_db)):
    tecnico = obtener_tecnico(db, id_tecnico)
    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado"
        )
    return {
        "id_tecnico": tecnico.id_tecnico,
        "id_taller": tecnico.id_taller,
        "especialidad": tecnico.especialidad,
        "estado_disponibilidad": tecnico.estado_disponibilidad,
        "latitud_actual": tecnico.latitud_actual,
        "longitud_actual": tecnico.longitud_actual,
        "nombre": tecnico.usuario.nombre,
        "correo": tecnico.usuario.correo,
        "telefono": tecnico.usuario.telefono
    }

@router.put("/{id_tecnico}", response_model=TecnicoRespuesta)
def actualizar(id_tecnico: int, datos: TecnicoActualizar, db: Session = Depends(get_db)):
    tecnico = actualizar_tecnico(db, id_tecnico, datos)
    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado"
        )
    return {
        "id_tecnico": tecnico.id_tecnico,
        "id_taller": tecnico.id_taller,
        "especialidad": tecnico.especialidad,
        "estado_disponibilidad": tecnico.estado_disponibilidad,
        "latitud_actual": tecnico.latitud_actual,
        "longitud_actual": tecnico.longitud_actual,
        "nombre": tecnico.usuario.nombre,
        "correo": tecnico.usuario.correo,
        "telefono": tecnico.usuario.telefono
    }

@router.patch("/{id_tecnico}/disponibilidad", response_model=TecnicoRespuesta)
def disponibilidad(id_tecnico: int, datos: CambiarDisponibilidad, db: Session = Depends(get_db)):
    tecnico = cambiar_disponibilidad(db, id_tecnico, datos.estado_disponibilidad)
    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado"
        )
    return {
        "id_tecnico": tecnico.id_tecnico,
        "id_taller": tecnico.id_taller,
        "especialidad": tecnico.especialidad,
        "estado_disponibilidad": tecnico.estado_disponibilidad,
        "latitud_actual": tecnico.latitud_actual,
        "longitud_actual": tecnico.longitud_actual,
        "nombre": tecnico.usuario.nombre,
        "correo": tecnico.usuario.correo,
        "telefono": tecnico.usuario.telefono
    }
@router.delete("/{id_tecnico}")
def eliminar_tecnico(id_tecnico: int, db: Session = Depends(get_db)):
    tecnico = obtener_tecnico(db, id_tecnico)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    # Eliminar usuario asociado también
    usuario = db.query(Usuario).filter(Usuario.id_usuario == tecnico.id_usuario).first()
    db.delete(tecnico)
    if usuario:
        db.delete(usuario)
    db.commit()
    return {"mensaje": "Técnico eliminado correctamente"}
@router.get("/por-usuario/{id_usuario}", response_model=TecnicoRespuesta)
def obtener_tecnico_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    tecnico = db.query(Tecnico).filter(Tecnico.id_usuario == id_usuario).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return {
        "id_tecnico": tecnico.id_tecnico,
        "id_taller": tecnico.id_taller,
        "especialidad": tecnico.especialidad,
        "estado_disponibilidad": tecnico.estado_disponibilidad,
        "latitud_actual": tecnico.latitud_actual,
        "longitud_actual": tecnico.longitud_actual,
        "nombre": tecnico.usuario.nombre,
        "correo": tecnico.usuario.correo,
        "telefono": tecnico.usuario.telefono,
        "nombre_taller": tecnico.taller.nombre_taller if tecnico.taller else None
    }
@router.get("/", response_model=List[TecnicoRespuesta])
def listar_todos_tecnicos(db: Session = Depends(get_db)):
    tecnicos = db.query(Tecnico).all()
    return [{
        "id_tecnico": t.id_tecnico,
        "id_taller": t.id_taller,
        "especialidad": t.especialidad,
        "estado_disponibilidad": t.estado_disponibilidad,
        "latitud_actual": t.latitud_actual,
        "longitud_actual": t.longitud_actual,
        "nombre": t.usuario.nombre,
        "correo": t.usuario.correo,
        "telefono": t.usuario.telefono,
        "nombre_taller": t.taller.nombre_taller if t.taller else '-'
    } for t in tecnicos]