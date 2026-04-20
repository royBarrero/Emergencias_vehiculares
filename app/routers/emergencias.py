from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.emergencia import TipoEvidenciaEnum
from app.models.conductor import Conductor
from app.schemas.emergencia import (
    EmergenciaCreate, EmergenciaOut,
    EmergenciaEstadoOut, EmergenciaResumen
)
from app.services import emergencia_service as svc

router = APIRouter(prefix="/emergencias", tags=["Emergencias"])


def get_conductor_actual(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> Conductor:
    conductor = db.query(Conductor).filter(Conductor.id_usuario == current_user.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=403, detail="Solo conductores pueden realizar esta acción")
    return conductor


# CU22 — Historial (VA PRIMERO, antes de cualquier ruta con /{id})
@router.get("/conductor/historial", response_model=List[EmergenciaResumen])
def historial(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    conductor: Conductor = Depends(get_conductor_actual),
):
    return svc.listar_emergencias_conductor(db, conductor.id_conductor, skip, limit)


# CU08 — Registrar emergencia
@router.post("/", response_model=EmergenciaOut, status_code=status.HTTP_201_CREATED)
def registrar_emergencia(
    data: EmergenciaCreate,
    db: Session = Depends(get_db),
    conductor: Conductor = Depends(get_conductor_actual),
):
    return svc.crear_emergencia(db, data, conductor.id_conductor)


# CU09 — Subir evidencia (foto o audio)
@router.post("/{id_emergencia}/evidencia", status_code=status.HTTP_201_CREATED)
async def subir_evidencia(
    id_emergencia: int,
    tipo: TipoEvidenciaEnum = Form(...),
    descripcion: Optional[str] = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    conductor: Conductor = Depends(get_conductor_actual),
):
    evidencia = await svc.agregar_evidencia(db, id_emergencia, tipo, archivo, descripcion)
    return {
        "mensaje": "Evidencia subida correctamente",
        "id_evidencia": evidencia.id_evidencia,
        "url": evidencia.url_archivo
    }


# CU19 — Estado de la emergencia (polling desde Flutter)
@router.get("/{id_emergencia}/estado", response_model=EmergenciaEstadoOut)
def obtener_estado(
    id_emergencia: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return svc.obtener_emergencia(db, id_emergencia)


# Detalle completo
@router.get("/{id_emergencia}", response_model=EmergenciaOut)
def obtener_emergencia_detalle(
    id_emergencia: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return svc.obtener_emergencia(db, id_emergencia)


# Cancelar emergencia
@router.delete("/{id_emergencia}", response_model=EmergenciaOut)
def cancelar_emergencia(
    id_emergencia: int,
    db: Session = Depends(get_db),
    conductor: Conductor = Depends(get_conductor_actual),
):
    return svc.cancelar_emergencia(db, id_emergencia, conductor.id_conductor)