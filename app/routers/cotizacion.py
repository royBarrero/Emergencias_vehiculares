from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cotizacion import Cotizacion, EstadoCotizacionEnum
from app.schemas.cotizacion import CotizacionSolicitar, CotizacionResponder, CotizacionRespuesta
from app.routers.auth import get_current_user
from typing import List
from app.websockets.connection_manager import manager

router = APIRouter(
    prefix="/cotizaciones",
    tags=["Cotizaciones"]
)

@router.post("/solicitar", response_model=CotizacionRespuesta)
async def solicitar_cotizacion(datos: CotizacionSolicitar, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    existente = db.query(Cotizacion).filter(
        Cotizacion.id_emergencia == datos.id_emergencia,
        Cotizacion.estado.in_([EstadoCotizacionEnum.solicitada, EstadoCotizacionEnum.enviada])
    ).first()
    if existente:
        return existente
    cotizacion = Cotizacion(
        id_emergencia=datos.id_emergencia,
        id_taller=datos.id_taller,
        estado=EstadoCotizacionEnum.solicitada
    )
    db.add(cotizacion)
    db.commit()
    db.refresh(cotizacion)

    # Notificar al taller via WebSocket
    await manager.broadcast_taller(datos.id_taller, {
        "tipo": "nueva_cotizacion",
        "id_emergencia": datos.id_emergencia,
        "id_cotizacion": cotizacion.id_cotizacion,
    })

    return cotizacion
@router.get("/emergencia/{id_emergencia}", response_model=CotizacionRespuesta)
def obtener_cotizacion(id_emergencia: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.emergencia import Emergencia
    emergencia = db.query(Emergencia).filter(Emergencia.id_emergencia == id_emergencia).first()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")

    query = db.query(Cotizacion).filter(
        Cotizacion.id_emergencia == id_emergencia,
        Cotizacion.estado.in_([
            EstadoCotizacionEnum.solicitada,
            EstadoCotizacionEnum.enviada,
            EstadoCotizacionEnum.aceptada
        ])
    )
    if emergencia.id_taller:
        query = query.filter(Cotizacion.id_taller == emergencia.id_taller)

    cotizacion = query.order_by(Cotizacion.created_at.desc()).first()
    if not cotizacion:
        raise HTTPException(status_code=404, detail="No hay cotización para esta emergencia")
    return cotizacion
@router.put("/{id_cotizacion}/responder", response_model=CotizacionRespuesta)
def responder_cotizacion(id_cotizacion: int, datos: CotizacionResponder, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cotizacion = db.query(Cotizacion).filter(Cotizacion.id_cotizacion == id_cotizacion).first()
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    cotizacion.monto_estimado = datos.monto_estimado
    cotizacion.descripcion_servicio = datos.descripcion_servicio
    cotizacion.tiempo_estimado = datos.tiempo_estimado
    cotizacion.observacion = datos.observacion
    cotizacion.estado = EstadoCotizacionEnum.enviada
    db.commit()
    db.refresh(cotizacion)
    return cotizacion

@router.patch("/{id_cotizacion}/decision")
async def decidir_cotizacion(id_cotizacion: int, decision: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cotizacion = db.query(Cotizacion).filter(Cotizacion.id_cotizacion == id_cotizacion).first()
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    accion = decision.get("accion")
    if accion == "aceptar":
        cotizacion.estado = EstadoCotizacionEnum.aceptada
    elif accion == "rechazar":
        cotizacion.estado = EstadoCotizacionEnum.rechazada
    else:
        raise HTTPException(status_code=400, detail="Acción inválida.")
    db.commit()
    db.refresh(cotizacion)

    # Notificar al taller via WebSocket
    await manager.broadcast_taller(cotizacion.id_taller, {
        "tipo": "decision_cotizacion",
        "id_emergencia": cotizacion.id_emergencia,
        "id_cotizacion": id_cotizacion,
        "estado": cotizacion.estado.value,
    })

    return {"mensaje": f"Cotización {cotizacion.estado}", "id_cotizacion": id_cotizacion}
@router.get("/taller/{id_taller}", response_model=List[CotizacionRespuesta])
def cotizaciones_por_taller(id_taller: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cotizaciones = db.query(Cotizacion).filter(
        Cotizacion.id_taller == id_taller
    ).order_by(Cotizacion.created_at.desc()).all()
    return cotizaciones

@router.delete("/emergencia/{id_emergencia}")
async def limpiar_cotizaciones_emergencia(id_emergencia: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Obtener id_taller antes de eliminar
    cotizacion = db.query(Cotizacion).filter(
        Cotizacion.id_emergencia == id_emergencia
    ).first()
    id_taller = cotizacion.id_taller if cotizacion else None

    db.query(Cotizacion).filter(
        Cotizacion.id_emergencia == id_emergencia
    ).delete()
    db.commit()

    # Notificar al taller via WebSocket
    if id_taller:
        await manager.broadcast_taller(id_taller, {
            "tipo": "decision_cotizacion",
            "id_emergencia": id_emergencia,
            "estado": "rechazada",
        })

    return {"mensaje": "Cotizaciones eliminadas correctamente"}