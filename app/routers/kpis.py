from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.emergencia import Emergencia, EstadoEmergenciaEnum
from app.models.taller import Taller
from app.models.tecnico import Tecnico
from app.models.pago import Pago
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/kpis", tags=["KPIs"])

def filtrar_por_fecha(query, modelo, fecha_inicio=None, fecha_fin=None):
    if fecha_inicio:
        query = query.filter(modelo.created_at >= fecha_inicio)
    if fecha_fin:
        query = query.filter(modelo.created_at <= fecha_fin)
    return query

@router.get("/taller/{id_taller}")
def kpis_taller(
    id_taller: int,
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    tipo_incidente: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query_base = db.query(Emergencia).filter(Emergencia.id_taller == id_taller)
    if fecha_inicio:
        query_base = query_base.filter(Emergencia.created_at >= fecha_inicio)
    if fecha_fin:
        query_base = query_base.filter(Emergencia.created_at <= fecha_fin)
    if tipo_incidente:
        query_base = query_base.filter(Emergencia.tipo_incidente == tipo_incidente)

    total = query_base.count()
    finalizadas = query_base.filter(Emergencia.estado == EstadoEmergenciaEnum.finalizada).count()
    canceladas = query_base.filter(Emergencia.estado == EstadoEmergenciaEnum.cancelada).count()

    # Tiempo promedio asignación (created_at → estado asignada usando updated_at)
    ems_asignadas = query_base.filter(
        Emergencia.estado.in_([
            EstadoEmergenciaEnum.asignada,
            EstadoEmergenciaEnum.en_camino,
            EstadoEmergenciaEnum.atendiendo,
            EstadoEmergenciaEnum.finalizada
        ]),
        Emergencia.updated_at != None
    ).all()

    tiempo_asignacion = 0
    if ems_asignadas:
        tiempos = [(e.updated_at - e.created_at).total_seconds() / 60 for e in ems_asignadas]
        tiempo_asignacion = round(sum(tiempos) / len(tiempos), 1)

    # SLA: emergencias atendidas en menos de 30 minutos
    sla_cumplido = sum(1 for e in ems_asignadas if (e.updated_at - e.created_at).total_seconds() / 60 <= 30)
    nivel_sla = round((sla_cumplido / len(ems_asignadas) * 100), 1) if ems_asignadas else 0

    # Incidentes por tipo
    por_tipo = db.query(
        Emergencia.tipo_incidente,
        func.count(Emergencia.id_emergencia).label('total')
    ).filter(Emergencia.id_taller == id_taller).group_by(Emergencia.tipo_incidente).all()

    # Técnicos más eficientes
    tecnicos = db.query(Tecnico).filter(Tecnico.id_taller == id_taller).all()
    tecnicos_data = []
    for t in tecnicos:
        atendidas = db.query(Emergencia).filter(
            Emergencia.id_tecnico == t.id_tecnico,
            Emergencia.estado == EstadoEmergenciaEnum.finalizada
        ).count()
        tecnicos_data.append({
            "id_tecnico": t.id_tecnico,
            "nombre": t.usuario.nombre,
            "emergencias_atendidas": atendidas,
            "calificacion": t.usuario.nombre  # placeholder
        })
    tecnicos_data.sort(key=lambda x: x["emergencias_atendidas"], reverse=True)

    # Ingresos
    pagos = db.query(func.sum(Pago.monto_total), func.sum(Pago.comision)).join(
        Emergencia, Pago.id_emergencia == Emergencia.id_emergencia
    ).filter(Emergencia.id_taller == id_taller).first()

    return {
        "total_emergencias": total,
        "finalizadas": finalizadas,
        "canceladas": canceladas,
        "tiempo_promedio_asignacion_min": tiempo_asignacion,
        "nivel_sla_pct": nivel_sla,
        "incidentes_por_tipo": [{"tipo": r[0], "total": r[1]} for r in por_tipo],
        "tecnicos_eficientes": tecnicos_data[:5],
        "ingresos_total": round(pagos[0] or 0, 2),
        "comision_total": round(pagos[1] or 0, 2),
    }

@router.get("/admin")
def kpis_admin(
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.id_rol != 4:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Solo superadmin")

    total = db.query(Emergencia).count()
    finalizadas = db.query(Emergencia).filter(Emergencia.estado == EstadoEmergenciaEnum.finalizada).count()
    canceladas = db.query(Emergencia).filter(Emergencia.estado == EstadoEmergenciaEnum.cancelada).count()

    # Por tenant
    from app.models.tenant import Tenant
    tenants = db.query(Tenant).all()
    por_tenant = []
    for t in tenants:
        talleres_ids = [taller.id_taller for taller in db.query(Taller).filter(Taller.id_tenant == t.id_tenant).all()]
        if talleres_ids:
            count = db.query(Emergencia).filter(Emergencia.id_taller.in_(talleres_ids)).count()
        else:
            count = 0
        por_tenant.append({"tenant": t.nombre, "total": count})

    # Ingresos globales
    pagos = db.query(func.sum(Pago.monto_total), func.sum(Pago.comision)).first()

    # Por tipo incidente
    por_tipo = db.query(
        Emergencia.tipo_incidente,
        func.count(Emergencia.id_emergencia).label('total')
    ).group_by(Emergencia.tipo_incidente).all()

    return {
        "total_emergencias": total,
        "finalizadas": finalizadas,
        "canceladas": canceladas,
        "tasa_completado_pct": round(finalizadas / total * 100, 1) if total else 0,
        "por_tenant": por_tenant,
        "incidentes_por_tipo": [{"tipo": r[0], "total": r[1]} for r in por_tipo],
        "ingresos_total": round(pagos[0] or 0, 2),
        "comision_total": round(pagos[1] or 0, 2),
    }
@router.get("/tenant/{id_tenant}")
def kpis_tenant(
    id_tenant: int,
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    talleres = db.query(Taller).filter(Taller.id_tenant == id_tenant).all()
    talleres_ids = [t.id_taller for t in talleres]

    if not talleres_ids:
        return {
            "total_emergencias": 0, "finalizadas": 0, "canceladas": 0,
            "tasa_completado_pct": 0, "ingresos_total": 0, "comision_total": 0,
            "por_taller": [], "incidentes_por_tipo": []
        }

    query_base = db.query(Emergencia).filter(Emergencia.id_taller.in_(talleres_ids))
    if fecha_inicio:
        query_base = query_base.filter(Emergencia.created_at >= fecha_inicio)
    if fecha_fin:
        query_base = query_base.filter(Emergencia.created_at <= fecha_fin)

    total = query_base.count()
    finalizadas = query_base.filter(Emergencia.estado == EstadoEmergenciaEnum.finalizada).count()
    canceladas = query_base.filter(Emergencia.estado == EstadoEmergenciaEnum.cancelada).count()

    # Por taller
    por_taller = []
    for t in talleres:
        count = db.query(Emergencia).filter(Emergencia.id_taller == t.id_taller).count()
        fin = db.query(Emergencia).filter(
            Emergencia.id_taller == t.id_taller,
            Emergencia.estado == EstadoEmergenciaEnum.finalizada
        ).count()
        por_taller.append({
            "nombre_taller": t.nombre_taller,
            "total": count,
            "finalizadas": fin,
            "calificacion": t.calificacion_promedio
        })

    por_taller.sort(key=lambda x: x["total"], reverse=True)

    # Por tipo
    por_tipo = db.query(
        Emergencia.tipo_incidente,
        func.count(Emergencia.id_emergencia).label('total')
    ).filter(Emergencia.id_taller.in_(talleres_ids)).group_by(Emergencia.tipo_incidente).all()

    # Ingresos
    pagos = db.query(func.sum(Pago.monto_total), func.sum(Pago.comision)).join(
        Emergencia, Pago.id_emergencia == Emergencia.id_emergencia
    ).filter(Emergencia.id_taller.in_(talleres_ids)).first()

    return {
        "total_emergencias": total,
        "finalizadas": finalizadas,
        "canceladas": canceladas,
        "tasa_completado_pct": round(finalizadas / total * 100, 1) if total else 0,
        "ingresos_total": round(pagos[0] or 0, 2),
        "comision_total": round(pagos[1] or 0, 2),
        "por_taller": por_taller,
        "incidentes_por_tipo": [{"tipo": r[0], "total": r[1]} for r in por_tipo],
    }