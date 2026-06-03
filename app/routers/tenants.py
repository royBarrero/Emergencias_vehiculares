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
        "estado": t.estado,
        "calificacion_promedio": t.calificacion_promedio,
        "id_tenant": t.id_tenant
    } for t in tenant.talleres]