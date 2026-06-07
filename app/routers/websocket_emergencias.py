from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.websockets.connection_manager import manager
from app.models.emergencia import Emergencia

router = APIRouter()

@router.websocket("/ws/emergencia/{id_emergencia}")
async def websocket_emergencia(
    websocket: WebSocket,
    id_emergencia: int,
    db: Session = Depends(get_db)
):
    await manager.connect(websocket, id_emergencia)
    try:
        # Enviar estado actual al conectarse
        emergencia = db.query(Emergencia).filter(
            Emergencia.id_emergencia == id_emergencia
        ).first()
        if emergencia:
            await websocket.send_json({
                "tipo": "estado_actual",
                "id_emergencia": id_emergencia,
                "estado": emergencia.estado.value,
                "id_tecnico": emergencia.id_tecnico,
                "id_taller": emergencia.id_taller,
                "tiempo_estimado_reparacion": emergencia.tiempo_estimado_reparacion,
            })
        # Mantener conexión viva
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, id_emergencia)

@router.websocket("/ws/taller/{id_taller}")
async def websocket_taller(
    websocket: WebSocket,
    id_taller: int,
    db: Session = Depends(get_db)
):
    await manager.connect_taller(websocket, id_taller)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_taller(websocket, id_taller)

