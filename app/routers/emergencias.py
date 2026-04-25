from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.emergencia import TipoEvidenciaEnum, Emergencia, EstadoEmergenciaEnum
from app.models.conductor import Conductor
from app.schemas.emergencia import (
    EmergenciaCreate, EmergenciaOut,
    EmergenciaEstadoOut, EmergenciaResumen,EmergenciaUpdate
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

@router.get("/pendientes", response_model=List[EmergenciaResumen])
def listar_pendientes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        db.query(Emergencia)
        .filter(Emergencia.estado == EstadoEmergenciaEnum.pendiente)
        .order_by(Emergencia.created_at.desc())
        .all()
    )


# Emergencias asignadas a un taller específico
@router.get("/taller/{id_taller}", response_model=List[EmergenciaResumen])
def listar_emergencias_taller(
    id_taller: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.tecnico import Tecnico
    from app.models.usuario import Usuario

    emergencias = (
        db.query(Emergencia)
        .filter(Emergencia.id_taller == id_taller)
        .order_by(Emergencia.created_at.desc())
        .all()
    )

    resultado = []
    for em in emergencias:
        nombre_tecnico = None
        if em.id_tecnico:
            tecnico = db.query(Tecnico).filter(Tecnico.id_tecnico == em.id_tecnico).first()
            if tecnico:
                usuario = db.query(Usuario).filter(Usuario.id_usuario == tecnico.id_usuario).first()
                if usuario:
                    nombre_tecnico = usuario.nombre

        resultado.append({
            "id_emergencia": em.id_emergencia,
            "id_taller": em.id_taller,
            "id_tecnico": em.id_tecnico,
            "nombre_tecnico": nombre_tecnico,
            "tipo_incidente": em.tipo_incidente,
            "prioridad": em.prioridad,
            "estado": em.estado,
            "direccion_aproximada": em.direccion_aproximada,
            "created_at": em.created_at,
        })

    return resultado
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

# Emergencias pendientes (para que el taller vea las disponibles)
# CU16/CU17/CU18 — Actualizar estado, asignar taller y técnico
@router.patch("/{id_emergencia}", response_model=EmergenciaOut)
def actualizar_emergencia(
    id_emergencia: int,
    datos: EmergenciaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return svc.actualizar_estado_emergencia(db, id_emergencia, datos.model_dump(exclude_unset=True))
# Cancelar emergencia
@router.delete("/{id_emergencia}", response_model=EmergenciaOut)
def cancelar_emergencia(
    id_emergencia: int,
    db: Session = Depends(get_db),
    conductor: Conductor = Depends(get_conductor_actual),
):
    return svc.cancelar_emergencia(db, id_emergencia, conductor.id_conductor)