from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.bitacora import Bitacora

router = APIRouter(
    prefix="/bitacora",
    tags=["Bitácora"]
)

@router.get("/tenant/{id_tenant}")
def obtener_bitacora_tenant(id_tenant: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    registros = db.query(Bitacora).filter(
        Bitacora.id_tenant == id_tenant
    ).order_by(Bitacora.fecha.desc()).all()
    return [{
        "id_bitacora": r.id_bitacora,
        "accion": r.accion,
        "descripcion": r.descripcion,
        "nombre_usuario": r.usuario.nombre,
        "ip_address": r.ip_address,
        "fecha": r.fecha
    } for r in registros]

@router.get("/")
def obtener_bitacora_completa(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.id_rol != 4:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Solo el superadmin puede ver la bitácora completa")
    registros = db.query(Bitacora).order_by(Bitacora.fecha.desc()).limit(500).all()
    return [{
        "id_bitacora": r.id_bitacora,
        "accion": r.accion,
        "descripcion": r.descripcion,
        "nombre_usuario": r.usuario.nombre,
        "ip_address": r.ip_address,
        "id_tenant": r.id_tenant,
        "fecha": r.fecha
    } for r in registros]