from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.rol import RolCrear, RolActualizar, RolRespuesta, AsignarRol
from app.services.rol_service import (
    obtener_roles, obtener_rol, crear_rol,
    actualizar_rol, asignar_rol
)

router = APIRouter(
    prefix="/roles",
    tags=["Roles y Permisos"]
)

@router.get("/", response_model=List[RolRespuesta])
def listar_roles(db: Session = Depends(get_db)):
    return obtener_roles(db)

@router.get("/{id_rol}", response_model=RolRespuesta)
def ver_rol(id_rol: int, db: Session = Depends(get_db)):
    rol = obtener_rol(db, id_rol)
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    return rol

@router.post("/", response_model=RolRespuesta)
def crear(datos: RolCrear, db: Session = Depends(get_db)):
    rol = crear_rol(db, datos)
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un rol con ese nombre"
        )
    return rol

@router.put("/{id_rol}", response_model=RolRespuesta)
def actualizar(id_rol: int, datos: RolActualizar, db: Session = Depends(get_db)):
    rol = actualizar_rol(db, id_rol, datos)
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    return rol

@router.post("/asignar")
def asignar(datos: AsignarRol, db: Session = Depends(get_db)):
    usuario = asignar_rol(db, datos.id_usuario, datos.id_rol)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario o rol no encontrado"
        )
    return {"mensaje": f"Rol asignado correctamente al usuario {usuario.nombre}"}