from pydantic import BaseModel
from typing import Optional

class VehiculoCrear(BaseModel):
    id_conductor: int
    marca: str
    modelo: str
    anio: Optional[int] = None
    placa: str
    color: Optional[str] = None
    tipo_vehiculo: Optional[str] = None

class VehiculoActualizar(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    color: Optional[str] = None
    tipo_vehiculo: Optional[str] = None

class VehiculoRespuesta(BaseModel):
    id_vehiculo: int
    id_conductor: int
    marca: str
    modelo: str
    anio: Optional[int] = None
    placa: str
    color: Optional[str] = None
    tipo_vehiculo: Optional[str] = None

    class Config:
        from_attributes = True