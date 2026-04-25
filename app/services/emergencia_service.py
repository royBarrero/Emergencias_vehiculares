from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.models.emergencia import Emergencia, EvidenciaEmergencia, EstadoEmergenciaEnum, TipoEvidenciaEnum
from app.schemas.emergencia import EmergenciaCreate
from typing import Optional
import uuid
import requests
from app.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET
from app.services.ia_service import transcribir_y_mejorar_audio, analizar_imagen_vehiculo

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
    obtener_emergencia(db, id_emergencia)

    # Leer contenido del archivo
    contenido = await file.read()
    extension = file.filename.split(".")[-1]
    folder = "fotos" if tipo == TipoEvidenciaEnum.foto else "audios"
    nombre_unico = f"{folder}/{uuid.uuid4()}.{extension}"

    # Subir a Supabase Storage via REST API
    url_upload = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{nombre_unico}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": file.content_type if file.content_type and file.content_type != "application/octet-stream" else f"image/{extension}" if tipo == TipoEvidenciaEnum.foto else "audio/m4a",
    }
    response = requests.post(url_upload, headers=headers, data=contenido)

    if response.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail="Error al subir archivo a Supabase")

    # URL pública del archivo
    url_archivo = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{nombre_unico}"

    # Procesar con IA
    transcripcion = None
    clasificacion_ia = None

    if tipo == TipoEvidenciaEnum.audio:
        transcripcion = transcribir_y_mejorar_audio(url_archivo)
        # Actualizar transcripción en la emergencia
        if transcripcion:
            em = obtener_emergencia(db, id_emergencia)
            em.transcripcion_audio = transcripcion
            db.commit()

    elif tipo == TipoEvidenciaEnum.foto:
            clasificacion_ia = analizar_imagen_vehiculo(url_archivo)

    evidencia = EvidenciaEmergencia(
            id_emergencia=id_emergencia,
            tipo=tipo,
            url_archivo=url_archivo,
            descripcion=descripcion,
            transcripcion=transcripcion,
            clasificacion_ia=clasificacion_ia,
        )
    db.add(evidencia)
    db.commit()
    db.refresh(evidencia)
    return evidencia
def actualizar_estado_emergencia(db: Session, id_emergencia: int, datos: dict) -> Emergencia:
    em = obtener_emergencia(db, id_emergencia)
    
    if 'estado' in datos:
        em.estado = datos['estado']
    if 'id_taller' in datos:
        em.id_taller = datos['id_taller']
    if 'id_tecnico' in datos:
        em.id_tecnico = datos['id_tecnico']
    
    db.commit()
    db.refresh(em)
    return em