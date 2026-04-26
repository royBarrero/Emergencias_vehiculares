from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.taller import TallerCrear, TallerActualizar, TallerRespuesta, ServicioCrear, ServicioRespuesta
from app.services.taller_service import (
    crear_taller, obtener_taller, obtener_todos_talleres,
    actualizar_taller, agregar_servicio
)
from app.models.taller import Taller
router = APIRouter(
    prefix="/talleres",
    tags=["Talleres"]
)

@router.post("/", response_model=TallerRespuesta)
def registrar_taller(datos: TallerCrear, db: Session = Depends(get_db)):
    taller = crear_taller(db, datos)
    if not taller:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )
    return {
        "id_taller": taller.id_taller,
        "nombre_taller": taller.nombre_taller,
        "direccion": taller.direccion,
        "latitud": taller.latitud,
        "longitud": taller.longitud,
        "telefono": taller.telefono,
        "descripcion": taller.descripcion,
        "estado": taller.estado,
        "calificacion_promedio": taller.calificacion_promedio,
        "nombre": taller.usuario.nombre,
        "correo": taller.usuario.correo,
        "servicios": taller.servicios
    }

@router.get("/", response_model=List[TallerRespuesta])
def listar_talleres(db: Session = Depends(get_db)):
    talleres = obtener_todos_talleres(db)
    return [{
        "id_taller": t.id_taller,
        "nombre_taller": t.nombre_taller,
        "direccion": t.direccion,
        "latitud": t.latitud,
        "longitud": t.longitud,
        "telefono": t.telefono,
        "descripcion": t.descripcion,
        "estado": t.estado,
        "calificacion_promedio": t.calificacion_promedio,
        "nombre": t.usuario.nombre,
        "correo": t.usuario.correo,
        "servicios": t.servicios
    } for t in talleres]

@router.get("/{id_taller}", response_model=TallerRespuesta)
def ver_taller(id_taller: int, db: Session = Depends(get_db)):
    taller = obtener_taller(db, id_taller)
    if not taller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Taller no encontrado"
        )
    return {
        "id_taller": taller.id_taller,
        "nombre_taller": taller.nombre_taller,
        "direccion": taller.direccion,
        "latitud": taller.latitud,
        "longitud": taller.longitud,
        "telefono": taller.telefono,
        "descripcion": taller.descripcion,
        "estado": taller.estado,
        "calificacion_promedio": taller.calificacion_promedio,
        "nombre": taller.usuario.nombre,
        "correo": taller.usuario.correo,
        "servicios": taller.servicios
    }

@router.put("/{id_taller}", response_model=TallerRespuesta)
def actualizar(id_taller: int, datos: TallerActualizar, db: Session = Depends(get_db)):
    taller = actualizar_taller(db, id_taller, datos)
    if not taller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Taller no encontrado"
        )
    return {
        "id_taller": taller.id_taller,
        "nombre_taller": taller.nombre_taller,
        "direccion": taller.direccion,
        "latitud": taller.latitud,
        "longitud": taller.longitud,
        "telefono": taller.telefono,
        "descripcion": taller.descripcion,
        "estado": taller.estado,
        "calificacion_promedio": taller.calificacion_promedio,
        "nombre": taller.usuario.nombre,
        "correo": taller.usuario.correo,
        "servicios": taller.servicios
    }

@router.post("/{id_taller}/servicios", response_model=ServicioRespuesta)
def agregar_servicio_taller(id_taller: int, datos: ServicioCrear, db: Session = Depends(get_db)):
    servicio = agregar_servicio(db, id_taller, datos)
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Taller no encontrado"
        )
    return servicio
@router.delete("/{id_taller}/servicios/{id_servicio}")
def eliminar_servicio_taller(id_taller: int, id_servicio: int, db: Session = Depends(get_db)):
    from app.models.servicio_taller import ServicioTaller
    servicio = db.query(ServicioTaller).filter(
        ServicioTaller.id_servicio == id_servicio,
        ServicioTaller.id_taller == id_taller
    ).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.delete(servicio)
    db.commit()
    return {"mensaje": "Servicio eliminado correctamente"}
@router.get("/cercanos/{id_emergencia}")
def talleres_cercanos(id_emergencia: int, db: Session = Depends(get_db)):
    from app.models.emergencia import Emergencia
    from app.models.servicio_taller import ServicioTaller
    import math

    emergencia = db.query(Emergencia).filter(Emergencia.id_emergencia == id_emergencia).first()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")

    def calcular_distancia(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    # Mapear tipo de incidente a servicio
    mapa_servicios = {
        'Pinchazo': 'Llantas y alineación',
        'Falla de motor': 'Motor',
        'Batería descargada': 'Electricidad automotriz',
        'Falla de frenos': 'Frenos',
        'Transmisión': 'Transmisión y caja',
        'Sobrecalentamiento': 'Motor',
        'Accidente': 'Chaperio y pintura',
    }

    servicio_requerido = mapa_servicios.get(emergencia.tipo_incidente)

    talleres = db.query(Taller).filter(Taller.estado == 'activo').all()
    resultado = []

    for t in talleres:
        if not t.latitud or not t.longitud:
            continue

        distancia = calcular_distancia(
            emergencia.latitud, emergencia.longitud,
            t.latitud, t.longitud
        )

        if distancia > 10:  # radio de 10km
            continue

        # Verificar si tiene el servicio requerido
        tiene_servicio = True
        if servicio_requerido:
            servicios = [s.nombre_servicio for s in t.servicios]
            tiene_servicio = servicio_requerido in servicios

        if not tiene_servicio:
            continue

        resultado.append({
            "id_taller": t.id_taller,
            "nombre_taller": t.nombre_taller,
            "direccion": t.direccion,
            "latitud": t.latitud,
            "longitud": t.longitud,
            "distancia_km": round(distancia, 2),
            "servicios": [s.nombre_servicio for s in t.servicios],
            "calificacion_promedio": t.calificacion_promedio
        })

    resultado.sort(key=lambda x: x["distancia_km"])
    return resultado
@router.get("/por-usuario/{id_usuario}", response_model=TallerRespuesta)
def obtener_taller_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    taller = db.query(Taller).filter(Taller.id_usuario == id_usuario).first()
    if not taller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Taller no encontrado"
        )
    return {
        "id_taller": taller.id_taller,
        "nombre_taller": taller.nombre_taller,
        "direccion": taller.direccion,
        "latitud": taller.latitud,
        "longitud": taller.longitud,
        "telefono": taller.telefono,
        "descripcion": taller.descripcion,
        "estado": taller.estado,
        "calificacion_promedio": taller.calificacion_promedio,
        "nombre": taller.usuario.nombre,
        "correo": taller.usuario.correo,
        "servicios": taller.servicios
    }
