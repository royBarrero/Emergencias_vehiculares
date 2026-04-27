from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional


class MetodoPagoEnum(str, Enum):
    efectivo = "efectivo"
    qr = "qr"

class EstadoPagoEnum(str, Enum):
    pendiente = "pendiente"
    completado = "completado"

class PagoCreate(BaseModel):
    id_emergencia: int
    monto_total: float
    metodo_pago: MetodoPagoEnum

class PagoOut(BaseModel):
    id_pago: int
    id_emergencia: int
    monto_total: float
    comision: float
    monto_neto: float
    metodo_pago: MetodoPagoEnum
    estado: EstadoPagoEnum
    created_at: datetime

    model_config = {"from_attributes": True}