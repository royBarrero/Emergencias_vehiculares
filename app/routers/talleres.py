from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.taller import TallerCrear, TallerActualizar, TallerRespuesta, ServicioCrear, ServicioRespuesta
from app.services.taller_service import (
    crear_taller, obtener_taller, obtener_todos_talleres,
    actualizar_taller, agregar_servicio
)
from app.routers.auth import get_current_user
from app.models.taller import Taller
from app.routers.bitacora import registrar_accion
router = APIRouter(
    prefix="/talleres",
    tags=["Talleres"]
)

@router.post("/", response_model=TallerRespuesta)
def registrar_taller(datos: TallerCrear, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    taller = crear_taller(db, datos)
    if not taller:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya está registrado")
    registrar_accion(db, current_user.id_usuario, current_user.tenant_id, "CREAR", f"Taller creado: {taller.nombre_taller}", request.client.host)
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
        "id_tenant": taller.id_tenant,
        "servicios": taller.servicios
    }

@router.get("/", response_model=List[TallerRespuesta])
def listar_talleres(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Superadmin ve todos, taller solo ve los de su tenant
    if current_user.id_rol == 4:
        talleres = obtener_todos_talleres(db)
    else:
        talleres = db.query(Taller).filter(Taller.id_tenant == current_user.tenant_id).all()
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
        "id_tenant": t.id_tenant,
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
        "id_tenant": taller.id_tenant,
        "servicios": taller.servicios
    }

@router.put("/{id_taller}", response_model=TallerRespuesta)
def actualizar(id_taller: int, datos: TallerActualizar, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    taller = actualizar_taller(db, id_taller, datos)
    if not taller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taller no encontrado")
    registrar_accion(db, current_user.id_usuario, current_user.tenant_id, "EDITAR", f"Taller editado: {taller.nombre_taller}", request.client.host)
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
        "id_tenant": taller.id_tenant,
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
def talleres_cercanos(id_emergencia: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
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

    # Filtrar talleres por tenant del conductor (usando tenant_id de la emergencia)
    query = db.query(Taller).filter(Taller.estado == 'activo')
    if current_user.tenant_id:
        query = query.filter(Taller.id_tenant == current_user.tenant_id)

    talleres = query.all()
    resultado = []

    for t in talleres:
        if not t.latitud or not t.longitud:
            continue
        distancia = calcular_distancia(
            emergencia.latitud, emergencia.longitud,
            t.latitud, t.longitud
        )
        if distancia > 10:
            continue
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
        "id_tenant": taller.id_tenant,
        "servicios": taller.servicios
    }

@router.patch("/{id_taller}/onesignal")
def actualizar_onesignal(id_taller: int, datos: dict, db: Session = Depends(get_db)):
    taller = db.query(Taller).filter(Taller.id_taller == id_taller).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    taller.onesignal_id = datos.get("onesignal_id")
    db.commit()
    return {"mensaje": "OneSignal ID actualizado"}

@router.post("/{id_taller}/calificar")
async def calificar_taller(
    id_taller: int,
    datos: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    from app.models.emergencia import Emergencia
    
    taller = db.query(Taller).filter(Taller.id_taller == id_taller).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    
    calificacion = datos.get("calificacion", 0)
    if calificacion < 1 or calificacion > 5:
        raise HTTPException(status_code=400, detail="Calificación debe ser entre 1 y 5")

    # Contar emergencias finalizadas para calcular promedio
    total = db.query(Emergencia).filter(
        Emergencia.id_taller == id_taller,
        Emergencia.estado == 'finalizada'
    ).count()

    if total <= 1:
        taller.calificacion_promedio = float(calificacion)
    else:
        promedio_actual = taller.calificacion_promedio or 0.0
        taller.calificacion_promedio = round(
            (promedio_actual * (total - 1) + calificacion) / total, 2
        )

    db.commit()
    return {
        "mensaje": "Calificación registrada",
        "nuevo_promedio": taller.calificacion_promedio
    }