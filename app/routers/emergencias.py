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
from app.models.taller import Taller
from app.websockets.connection_manager import manager
from app.services.notificaciones_service import enviar_notificacion
from app.models.conductor import Conductor
from app.services.notificaciones_service import enviar_notificacion, enviar_notificacion_taller

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
async def registrar_emergencia(
    data: EmergenciaCreate,
    db: Session = Depends(get_db),
    conductor: Conductor = Depends(get_conductor_actual),
):
    emergencia = svc.crear_emergencia(db, data, conductor.id_conductor)
    
    # Notificar a todos los talleres activos
    talleres = db.query(Taller).filter(Taller.estado == 'activo').all()
    for taller in talleres:
        await manager.broadcast_taller(taller.id_taller, {
            "tipo": "nueva_emergencia",
            "id_emergencia": emergencia.id_emergencia,
            "tipo_incidente": emergencia.tipo_incidente,
            "prioridad": emergencia.prioridad,
            "direccion_aproximada": emergencia.direccion_aproximada,
            "latitud": emergencia.latitud,
            "longitud": emergencia.longitud,
        })
        # Notificar a talleres via OneSignal
        for taller in talleres:
            if taller.onesignal_id:
                enviar_notificacion_taller(
                    taller.onesignal_id,
                    '🚨 Nueva emergencia',
                    f'Tipo: {emergencia.tipo_incidente} — {emergencia.direccion_aproximada or "Sin dirección"}',
                    {"id_emergencia": str(emergencia.id_emergencia)}
                )
    
    return emergencia


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
async def actualizar_emergencia(
    id_emergencia: int,
    datos: EmergenciaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    emergencia = svc.actualizar_estado_emergencia(db, id_emergencia, datos.model_dump(exclude_unset=True))

    await manager.broadcast(id_emergencia, {
        "tipo": "cambio_estado",
        "id_emergencia": id_emergencia,
        "estado": emergencia.estado.value,
        "id_tecnico": emergencia.id_tecnico,
        "id_taller": emergencia.id_taller,
    })
    # Notificar al taller via WebSocket
    if emergencia.id_taller:
        await manager.broadcast_taller(emergencia.id_taller, {
            "tipo": "cambio_estado",
            "id_emergencia": id_emergencia,
            "estado": emergencia.estado.value,
            "id_tecnico": emergencia.id_tecnico,
            "id_taller": emergencia.id_taller,
        })
    # Enviar notificación push al conductor
    try:
        conductor = db.query(Conductor).filter(
            Conductor.id_conductor == emergencia.id_conductor
        ).first()
        if conductor and conductor.fcm_token:
            mensajes = {
                'asignada': ('✅ Taller asignado', 'Un taller aceptó tu solicitud de emergencia'),
                'en_camino': ('🚗 Técnico en camino', 'El técnico está en camino a tu ubicación'),
                'atendiendo': ('🔧 En atención', 'El técnico está atendiendo tu vehículo'),
                'finalizada': ('✅ Servicio finalizado', 'Tu emergencia fue atendida exitosamente'),
                'cancelada': ('❌ Cancelado', 'La emergencia fue cancelada'),
            }
            estado = emergencia.estado.value
            if estado in mensajes:
                titulo, cuerpo = mensajes[estado]
                enviar_notificacion(
                    conductor.fcm_token,
                    titulo,
                    cuerpo,
                    {"id_emergencia": str(id_emergencia), "estado": estado}
                )
    except Exception as e:
        print(f"Error enviando push: {e}")

    return emergencia
@router.get("/tecnico/{id_tecnico}/historial", response_model=List[EmergenciaResumen])
def historial_tecnico(
    id_tecnico: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        db.query(Emergencia)
        .filter(
            Emergencia.id_tecnico == id_tecnico,
            Emergencia.estado == EstadoEmergenciaEnum.finalizada
        )
        .order_by(Emergencia.created_at.desc())
        .all()
    )
@router.get("/tecnico/{id_tecnico}", response_model=Optional[EmergenciaOut])
def obtener_emergencia_tecnico(
    id_tecnico: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    em = (
        db.query(Emergencia)
        .filter(
            Emergencia.id_tecnico == id_tecnico,
            Emergencia.estado.in_([
                EstadoEmergenciaEnum.asignada,
                EstadoEmergenciaEnum.en_camino,
                EstadoEmergenciaEnum.atendiendo
            ])
        )
        .order_by(Emergencia.created_at.desc())
        .first()
    )
    return em
@router.delete("/{id_emergencia}", response_model=EmergenciaOut)
async def cancelar_emergencia(
    id_emergencia: int,
    db: Session = Depends(get_db),
    conductor: Conductor = Depends(get_conductor_actual),
):
    emergencia = svc.cancelar_emergencia(db, id_emergencia, conductor.id_conductor)
    
    # Broadcast WebSocket
    await manager.broadcast(id_emergencia, {
        "tipo": "cambio_estado",
        "id_emergencia": id_emergencia,
        "estado": "cancelada",
        "id_tecnico": emergencia.id_tecnico,
        "id_taller": emergencia.id_taller,
    })

    # Notificar al taller via OneSignal
    if emergencia.id_taller:
        taller = db.query(Taller).filter(Taller.id_taller == emergencia.id_taller).first()
        if taller and taller.onesignal_id:
            enviar_notificacion_taller(
                taller.onesignal_id,
                '❌ Emergencia cancelada',
                'El conductor canceló la solicitud de servicio',
                {"id_emergencia": str(id_emergencia)}
            )

    return emergencia