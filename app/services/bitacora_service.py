from sqlalchemy.orm import Session
from app.models.bitacora import Bitacora

def registrar_evento(db: Session, id_usuario: int, accion: str, descripcion: str = None, ip_address: str = None, id_tenant: int = None):
    registro = Bitacora(
        id_usuario=id_usuario,
        accion=accion,
        descripcion=descripcion,
        ip_address=ip_address,
        id_tenant=id_tenant
    )
    db.add(registro)
    db.commit()