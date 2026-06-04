from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CotizacionSolicitar(BaseModel):
    id_emergencia: int
    id_taller: int

class CotizacionResponder(BaseModel):
    monto_estimado: float
    descripcion_servicio: str
    tiempo_estimado: str
    observacion: Optional[str] = None

class CotizacionRespuesta(BaseModel):
    id_cotizacion: int
    id_emergencia: int
    id_taller: int
    monto_estimado: Optional[float]
    descripcion_servicio: Optional[str]
    tiempo_estimado: Optional[str]
    observacion: Optional[str]
    estado: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True