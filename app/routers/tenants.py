from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.tenant import Tenant
from app.models.taller import Taller

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"]
)

def verificar_superadmin(current_user=Depends(get_current_user)):
    if current_user.id_rol != 4:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el superadmin puede realizar esta acción"
        )
    return current_user

@router.get("/")
def listar_tenants(db: Session = Depends(get_db), current_user=Depends(verificar_superadmin)):
    tenants = db.query(Tenant).all()
    return [{
        "id_tenant": t.id_tenant,
        "nombre": t.nombre,
        "descripcion": t.descripcion,
        "estado": t.estado,
        "fecha_creacion": t.fecha_creacion,
        "total_talleres": len(t.talleres)
    } for t in tenants]

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_tenant(datos: dict, db: Session = Depends(get_db), current_user=Depends(verificar_superadmin)):
    tenant = Tenant(
        nombre=datos.get("nombre"),
        descripcion=datos.get("descripcion"),
        estado=True
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

@router.get("/{id_tenant}")
def obtener_tenant(id_tenant: int, db: Session = Depends(get_db), current_user=Depends(verificar_superadmin)):
    tenant = db.query(Tenant).filter(Tenant.id_tenant == id_tenant).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return {
        "id_tenant": tenant.id_tenant,
        "nombre": tenant.nombre,
        "descripcion": tenant.descripcion,
        "estado": tenant.estado,
        "fecha_creacion": tenant.fecha_creacion,
        "talleres": [{
            "id_taller": t.id_taller,
            "nombre_taller": t.nombre_taller,
            "estado": t.estado,
            "calificacion_promedio": t.calificacion_promedio
        } for t in tenant.talleres]
    }

@router.patch("/{id_tenant}")
def actualizar_tenant(id_tenant: int, datos: dict, db: Session = Depends(get_db), current_user=Depends(verificar_superadmin)):
    tenant = db.query(Tenant).filter(Tenant.id_tenant == id_tenant).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    for key, value in datos.items():
        setattr(tenant, key, value)
    db.commit()
    db.refresh(tenant)
    return tenant

@router.delete("/{id_tenant}")
def eliminar_tenant(id_tenant: int, db: Session = Depends(get_db), current_user=Depends(verificar_superadmin)):
    tenant = db.query(Tenant).filter(Tenant.id_tenant == id_tenant).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    db.delete(tenant)
    db.commit()
    return {"mensaje": "Tenant eliminado correctamente"}

@router.post("/{id_tenant}/admin")
def asignar_admin_tenant(id_tenant: int, datos: dict, db: Session = Depends(get_db), current_user=Depends(verificar_superadmin)):
    from app.models.usuario import Usuario
    from app.services.auth_service import registrar_usuario

    # Crear usuario con rol 5
    nuevo_usuario = registrar_usuario(
        db,
        datos.get("nombre"),
        datos.get("correo"),
        datos.get("contrasena"),
        datos.get("telefono"),
        5
    )
    if not nuevo_usuario:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # Asignar como admin del tenant
    tenant = db.query(Tenant).filter(Tenant.id_tenant == id_tenant).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    tenant.id_usuario_admin = nuevo_usuario.id_usuario
    db.commit()

    return {
        "mensaje": "Admin de tenant creado correctamente",
        "id_usuario": nuevo_usuario.id_usuario,
        "correo": nuevo_usuario.correo,
        "id_tenant": id_tenant
    }
@router.get("/por-admin/{id_usuario}")
def obtener_tenant_por_admin(id_usuario: int, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id_usuario_admin == id_usuario).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return {
        "id_tenant": tenant.id_tenant,
        "nombre": tenant.nombre,
        "descripcion": tenant.descripcion,
        "estado": tenant.estado,
        "total_talleres": len(tenant.talleres)
    }
@router.get("/{id_tenant}/talleres")
def listar_talleres_tenant(id_tenant: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tenant = db.query(Tenant).filter(Tenant.id_tenant == id_tenant).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return [{
        "id_taller": t.id_taller,
        "nombre_taller": t.nombre_taller,
        "direccion": t.direccion,
        "telefono": t.telefono,
        "descripcion": t.descripcion,
        "estado": t.estado,
        "calificacion_promedio": t.calificacion_promedio,
        "id_tenant": t.id_tenant,
        "latitud": t.latitud,
        "longitud": t.longitud
    } for t in tenant.talleres]
@router.get("/{id_tenant}/talleres/{id_taller}/detalle")
def detalle_taller_tenant(id_tenant: int, id_taller: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    taller = db.query(Taller).filter(
        Taller.id_taller == id_taller,
        Taller.id_tenant == id_tenant
    ).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    return {
        "id_taller": taller.id_taller,
        "nombre_taller": taller.nombre_taller,
        "direccion": taller.direccion,
        "telefono": taller.telefono,
        "descripcion": taller.descripcion,
        "estado": taller.estado,
        "calificacion_promedio": taller.calificacion_promedio,
        "latitud": taller.latitud,
        "longitud": taller.longitud,
        "id_tenant": taller.id_tenant,
        "encargado": {
            "nombre": taller.usuario.nombre,
            "correo": taller.usuario.correo,
            "telefono": taller.usuario.telefono
        }
    }
@router.patch("/{id_tenant}/talleres/{id_taller}")
def editar_taller_tenant(id_tenant: int, id_taller: int, datos: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.id_rol not in [4, 5]:
        raise HTTPException(status_code=403, detail="Sin permisos")
    taller = db.query(Taller).filter(
        Taller.id_taller == id_taller,
        Taller.id_tenant == id_tenant
    ).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    campos = ["nombre_taller", "direccion", "telefono", "descripcion", "estado", "latitud", "longitud"]
    for campo in campos:
        if campo in datos:
            setattr(taller, campo, datos[campo])
    db.commit()
    db.refresh(taller)
    return {"mensaje": "Taller actualizado correctamente"}
@router.post("/{id_tenant}/talleres")
def crear_taller_tenant(id_tenant: int, datos: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.id_rol not in [4, 5]:
        raise HTTPException(status_code=403, detail="Sin permisos")
    from app.models.usuario import Usuario
    from app.models.servicio_taller import ServicioTaller
    from app.services.auth_service import registrar_usuario, encriptar_contrasena

    # Buscar usuario existente o crear nuevo
    if datos.get("correo_existente"):
        usuario = db.query(Usuario).filter(Usuario.correo == datos.get("correo_existente")).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    else:
        usuario = registrar_usuario(
            db,
            datos.get("nombre_admin"),
            datos.get("correo_admin"),
            datos.get("contrasena_admin"),
            datos.get("telefono_admin"),
            2
        )
        if not usuario:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")

    nuevo_taller = Taller(
        id_usuario=usuario.id_usuario,
        nombre_taller=datos.get("nombre_taller"),
        direccion=datos.get("direccion"),
        latitud=datos.get("latitud"),
        longitud=datos.get("longitud"),
        telefono=datos.get("telefono"),
        descripcion=datos.get("descripcion"),
        estado="activo",
        id_tenant=id_tenant
    )
    db.add(nuevo_taller)
    db.commit()
    db.refresh(nuevo_taller)

    for servicio in datos.get("servicios", []):
        db.add(ServicioTaller(
            id_taller=nuevo_taller.id_taller,
            nombre_servicio=servicio,
            disponible=True
        ))
    db.commit()

    return {
        "mensaje": "Taller creado correctamente",
        "id_taller": nuevo_taller.id_taller
    }