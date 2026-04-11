from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.vehiculo import VehiculoCrear, VehiculoActualizar, VehiculoRespuesta
from app.services.vehiculo_service import (
    crear_vehiculo, obtener_vehiculos_conductor,
    obtener_vehiculo, actualizar_vehiculo, eliminar_vehiculo
)

router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehículos"]
)

@router.post("/", response_model=VehiculoRespuesta)
def registrar_vehiculo(datos: VehiculoCrear, db: Session = Depends(get_db)):
    vehiculo = crear_vehiculo(db, datos)
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La placa ya está registrada"
        )
    return vehiculo

@router.get("/conductor/{id_conductor}", response_model=List[VehiculoRespuesta])
def listar_vehiculos(id_conductor: int, db: Session = Depends(get_db)):
    return obtener_vehiculos_conductor(db, id_conductor)

@router.get("/{id_vehiculo}", response_model=VehiculoRespuesta)
def ver_vehiculo(id_vehiculo: int, db: Session = Depends(get_db)):
    vehiculo = obtener_vehiculo(db, id_vehiculo)
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    return vehiculo

@router.put("/{id_vehiculo}", response_model=VehiculoRespuesta)
def actualizar(id_vehiculo: int, datos: VehiculoActualizar, db: Session = Depends(get_db)):
    vehiculo = actualizar_vehiculo(db, id_vehiculo, datos)
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    return vehiculo

@router.delete("/{id_vehiculo}")
def eliminar(id_vehiculo: int, db: Session = Depends(get_db)):
    resultado = eliminar_vehiculo(db, id_vehiculo)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    return {"mensaje": "Vehículo eliminado correctamente"}