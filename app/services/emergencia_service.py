from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.models.emergencia import Emergencia, EvidenciaEmergencia, EstadoEmergenciaEnum, TipoEvidenciaEnum
from app.schemas.emergencia import EmergenciaCreate
from typing import Optional
import shutil
import os
import uuid

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def crear_emergencia(db: Session, data: EmergenciaCreate, id_conductor: int) -> Emergencia:
    emergencia = Emergencia(
        id_conductor=id_conductor,
        id_vehiculo=data.id_vehiculo,
        latitud=data.latitud,
        longitud=data.longitud,
        direccion_aproximada=data.direccion_aproximada,
        tipo_incidente=data.tipo_incidente,
        prioridad=data.prioridad,
        descripcion=data.descripcion,
        estado=EstadoEmergenciaEnum.pendiente,
    )
    db.add(emergencia)
    db.commit()
    db.refresh(emergencia)
    return emergencia


def obtener_emergencia(db: Session, id_emergencia: int) -> Emergencia:
    em = db.query(Emergencia).filter(Emergencia.id_emergencia == id_emergencia).first()
    if not em:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergencia no encontrada")
    return em


def listar_emergencias_conductor(db: Session, id_conductor: int, skip: int = 0, limit: int = 20):
    return (
        db.query(Emergencia)
        .filter(Emergencia.id_conductor == id_conductor)
        .order_by(Emergencia.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def cancelar_emergencia(db: Session, id_emergencia: int, id_conductor: int) -> Emergencia:
    em = obtener_emergencia(db, id_emergencia)
    if em.id_conductor != id_conductor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    if em.estado in (EstadoEmergenciaEnum.finalizada, EstadoEmergenciaEnum.cancelada):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se puede cancelar en estado '{em.estado}'")
    em.estado = EstadoEmergenciaEnum.cancelada
    db.commit()
    db.refresh(em)
    return em


async def agregar_evidencia(
    db: Session,
    id_emergencia: int,
    tipo: TipoEvidenciaEnum,
    file: UploadFile,
    descripcion: Optional[str] = None,
) -> EvidenciaEmergencia:
    obtener_emergencia(db, id_emergencia)  # valida que exista

    # Guardar archivo en disco (carpeta uploads/)
    extension = file.filename.split(".")[-1]
    nombre_unico = f"{uuid.uuid4()}.{extension}"
    ruta_archivo = os.path.join(UPLOAD_DIR, nombre_unico)

    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    url_archivo = f"/uploads/{nombre_unico}"

    evidencia = EvidenciaEmergencia(
        id_emergencia=id_emergencia,
        tipo=tipo,
        url_archivo=url_archivo,
        descripcion=descripcion,
    )
    db.add(evidencia)
    db.commit()
    db.refresh(evidencia)
    return evidencia