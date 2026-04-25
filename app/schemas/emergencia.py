from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PrioridadEnum(str, Enum):
    baja = "baja"
    media = "media"
    alta = "alta"


class EstadoEmergenciaEnum(str, Enum):
    pendiente = "pendiente"
    buscando_taller = "buscando_taller"
    asignada = "asignada"
    en_camino = "en_camino"
    atendiendo = "atendiendo"
    finalizada = "finalizada"
    cancelada = "cancelada"


class TipoEvidenciaEnum(str, Enum):
    foto = "foto"
    audio = "audio"


# ── Evidencia ──────────────────────────────────────────────────

class EvidenciaOut(BaseModel):
    id_evidencia: int
    tipo: TipoEvidenciaEnum
    url_archivo: str
    descripcion: Optional[str]
    transcripcion: Optional[str]
    clasificacion_ia: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Emergencia ─────────────────────────────────────────────────

class EmergenciaCreate(BaseModel):
    id_vehiculo: int
    latitud: float
    longitud: float
    direccion_aproximada: Optional[str] = None
    tipo_incidente: str
    prioridad: PrioridadEnum = PrioridadEnum.media
    descripcion: Optional[str] = None


class EmergenciaOut(BaseModel):
    id_emergencia: int
    id_conductor: int
    id_vehiculo: int
    latitud: float
    longitud: float
    direccion_aproximada: Optional[str]
    tipo_incidente: str
    prioridad: PrioridadEnum
    descripcion: Optional[str]
    transcripcion_audio: Optional[str]
    estado: EstadoEmergenciaEnum
    evidencias: List[EvidenciaOut] = []
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class EmergenciaEstadoOut(BaseModel):
    """Respuesta liviana para el seguimiento (polling desde Flutter)"""
    id_emergencia: int
    estado: EstadoEmergenciaEnum
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class EmergenciaResumen(BaseModel):
    """Para el historial del conductor"""
    id_emergencia: int
    id_taller: Optional[int] = None
    id_tecnico: Optional[int] = None
    nombre_tecnico: Optional[str] = None
    tipo_incidente: str
    prioridad: PrioridadEnum
    estado: EstadoEmergenciaEnum
    direccion_aproximada: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

class EmergenciaUpdate(BaseModel):
    estado: Optional[EstadoEmergenciaEnum] = None
    id_taller: Optional[int] = None
    id_tecnico: Optional[int] = None
    